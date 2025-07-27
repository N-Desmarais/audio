import logging
import threading
from typing import Any, List

import numpy as np
import sounddevice as sd  
from scipy.io import wavfile  

BUFFER_BLOCKSIZE = 1024


class RingBuffer:
    """
    Thread-safe ring buffer for storing audio data.
    """

    def __init__(self, size: int, channels: int) -> None:
        """
        Initialize the ring buffer with the given size and channel count.

        Parameters:
            size (int): The number of frames in the buffer.
            channels (int): The number of audio channels.
        """
        self.size = size
        self.channels = channels
        self.buffer = np.zeros((size, channels), dtype=np.float32)
        self.write_index = 0
        self.read_index = 0
        self.filled = 0
        self.lock = threading.Lock()

    def write(self, data: np.ndarray) -> None:
        """
        Write audio data to the ring buffer.

        Parameters:
            data (np.ndarray): Audio data to write (frames, channels).
        """
        with self.lock:
            n = data.shape[0]
            end_index = self.size - self.write_index
            if n <= end_index:
                self.buffer[self.write_index:self.write_index + n] = data
            else:
                self.buffer[self.write_index:] = data[:end_index]
                self.buffer[:n - end_index] = data[end_index:]
            self.write_index = (self.write_index + n) % self.size
            # Overwrite: move read_index forward as well
            if self.filled + n > self.size:
                self.read_index = (self.read_index + (n - (self.size - self.filled))) % self.size
            self.filled = min(self.size, self.filled + n)

    def read(self, n: int) -> np.ndarray:
        """
        Read up to n frames from the ring buffer.

        Parameters:
            n (int): The number of frames to read.

        Returns:
            np.ndarray: The audio data read from the buffer (n, channels).
        """
        with self.lock:
            to_read = min(n, self.filled)
            end_index = self.size - self.read_index
            out = np.zeros((n, self.channels), dtype=np.float32)
            if to_read <= end_index:
                out[:to_read] = self.buffer[self.read_index:self.read_index + to_read]
            else:
                out[:end_index] = self.buffer[self.read_index:]
                out[end_index:to_read] = self.buffer[:to_read - end_index]
            self.read_index = (self.read_index + to_read) % self.size
            self.filled -= to_read
            return out


def audio_passthrough(
    input_idx: int,
    output_idx: int,
    sr: int,
    in_ch: int,
    out_ch: int,
    recorded_frames: List[np.ndarray],
    waveform_queue: Any,
    stop_event: threading.Event,
    save_recording: bool = False
) -> None:
    """
    Pass audio from the input device to the output device in real time, optionally recording.

    Parameters:
        input_idx (int): The input device index.
        output_idx (int): The output device index.
        sr (int): The sample rate.
        in_ch (int): The number of input channels.
        out_ch (int): The number of output channels.
        recorded_frames (List[np.ndarray]): List to store recorded audio frames.
        waveform_queue (Any): Queue for waveform data.
        stop_event (threading.Event): Event to signal stop.
        save_recording (bool): Whether to save the recording.
    """
    ring = RingBuffer(BUFFER_BLOCKSIZE * 8, in_ch)

    def input_callback(indata: np.ndarray, _frames: int, _time: Any, status: Any) -> None:
        if stop_event.is_set():
            return
        if status:
            logging.warning(f"Input stream status: {status}")
        if save_recording:
            recorded_frames.append(indata.copy())
        mono = np.mean(indata, axis=1)
        waveform_queue.put(mono)
        ring.write(indata)

    def output_callback(outdata: np.ndarray, frames: int, _time: Any, status: Any) -> None:
        if stop_event.is_set():
            return
        if status:
            logging.warning(f"Output stream status: {status}")
        data = ring.read(frames)
        outdata[:, :in_ch] = data
        if out_ch > in_ch:
            outdata[:, in_ch:] = 0

    with sd.InputStream(
        device=input_idx,
        channels=in_ch,
        samplerate=sr,
        blocksize=BUFFER_BLOCKSIZE,
        callback=input_callback
    ), sd.OutputStream(
        device=output_idx,
        channels=out_ch,
        samplerate=sr,
        blocksize=BUFFER_BLOCKSIZE,
        callback=output_callback
    ):
        while not stop_event.is_set():
            sd.sleep(100)


def audio_record(
    input_idx: int,
    sr: int,
    in_ch: int,
    recorded_frames: List[np.ndarray],
    waveform_queue: Any,
    stop_event: threading.Event
) -> None:
    """
    Record audio from the input device and send waveform data to the queue.

    Parameters:
        input_idx (int): The input device index.
        sr (int): The sample rate.
        in_ch (int): The number of input channels.
        recorded_frames (List[np.ndarray]): List to store recorded audio frames.
        waveform_queue (Any): Queue for waveform data.
        stop_event (threading.Event): Event to signal stop.
    """
    def input_callback(indata: np.ndarray, frames: int, time: Any, status: Any) -> None:
        if status:
            logging.warning(f"Input stream status: {status}")
        if stop_event.is_set():
            return
        recorded_frames.append(indata.copy())
        mono = np.mean(indata, axis=1)
        waveform_queue.put(mono)

    with sd.InputStream(
        device=input_idx,
        channels=in_ch,
        samplerate=sr,
        blocksize=BUFFER_BLOCKSIZE,
        callback=input_callback
    ):
        while not stop_event.is_set():
            sd.sleep(100)


def audio_playback(
    output_idx: int,
    out_ch: int,
    wav_path: str,
    stop_event: threading.Event,
    waveform_queue: Any
) -> None:
    """
    Play back a WAV file to the output device and send waveform data to the queue.

    Parameters:
        output_idx (int): The output device index.
        out_ch (int): The number of output channels.
        wav_path (str): Path to the WAV file.
        stop_event (threading.Event): Event to signal stop.
        waveform_queue (Any): Queue for waveform data.
    """
    try:
        wav_sr, data = wavfile.read(wav_path)
        if data.dtype != np.float32:
            # Convert to float32 in range [-1, 1]
            if np.issubdtype(data.dtype, np.integer):
                max_val = np.iinfo(data.dtype).max
                data = data.astype(np.float32) / max_val
            else:
                data = data.astype(np.float32)
        if data.ndim == 1:
            data = data[:, np.newaxis]
        if data.shape[1] < out_ch:
            # Pad with zeros for missing channels
            data = np.pad(data, ((0, 0), (0, out_ch - data.shape[1])))
        elif data.shape[1] > out_ch:
            data = data[:, :out_ch]
        total_frames = data.shape[0]
        frame_index = 0

        def output_callback(outdata: np.ndarray, frames: int, time: Any, status: Any) -> None:
            if stop_event.is_set():
                return
            nonlocal frame_index
            if status:
                logging.warning(f"Output stream status: {status}")
            end = min(frame_index + frames, total_frames)
            chunk = data[frame_index:end]
            out_len = end - frame_index
            if out_len < frames:
                outdata[:out_len] = chunk
                outdata[out_len:] = 0
                stop_event.set()
            else:
                outdata[:] = chunk
            # Send mono waveform to visualizer
            mono = np.mean(chunk, axis=1) if chunk.shape[1] > 1 else chunk[:, 0]
            waveform_queue.put(mono)
            frame_index = end

        with sd.OutputStream(
            device=output_idx,
            channels=out_ch,
            samplerate=wav_sr,  # Use the WAV file's sample rate
            blocksize=BUFFER_BLOCKSIZE,
            callback=output_callback
        ):
            while not stop_event.is_set() and frame_index < total_frames:
                sd.sleep(100)
    except Exception as e:
        logging.error(f"Playback error: {e}")