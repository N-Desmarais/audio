import logging
import multiprocessing
import signal
import threading
from typing import Any, List, Optional

import numpy as np
from scipy.io import wavfile

from arg_parser import get_config
from signal_processing.audio_io import audio_passthrough, audio_playback, audio_record
from file_utils import save_recording
from visualizer.visualizer import start_visualizer_process
from message_bus import MessageBus

def setup_logging(level: str) -> None:
    """
    Set up logging for the application.

    Parameters:
        level (str): The logging level as a string.
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='[%(levelname)s] %(message)s'
    )

def get_visualizer_sr(args: Any) -> int:
    """
    Determine the sample rate to use for the visualizer.

    Parameters:
        args (Any): The parsed command-line arguments.

    Returns:
        int: The sample rate to use.
    """
    if args.mode == "playback":
        wav_sr, _ = wavfile.read(args.wav_path)
        return wav_sr
    else:
        return args.sr

def setup_signal_handlers(audio_stop_event: Any, vis_stop_event: Any) -> None:
    """
    Set up signal handlers for clean shutdown on Ctrl+C.

    Parameters:
        audio_stop_event (threading.Event): Event to signal audio shutdown.
        vis_stop_event (threading.Event): Event to signal visualizer shutdown.
    """
    def handle(sig, frame):
        logging.info("Ctrl+C received, stopping...")
        audio_stop_event.set()
        vis_stop_event.set()
    signal.signal(signal.SIGINT, handle)

def start_audio_thread(
    args: Any,
    recorded_frames: List[np.ndarray],
    vis_waveform_queue: Any,
    audio_stop_event: threading.Event,
    message_bus: MessageBus
) -> Optional[threading.Thread]:
    """
    Start the audio processing thread for the selected mode.

    Parameters:
        args (Any): The parsed command-line arguments.
        recorded_frames (List[np.ndarray]): List to store recorded audio frames.
        vis_waveform_queue (Any): Queue for waveform data.
        audio_stop_event (threading.Event): Event to signal audio shutdown.

    Returns:
        Optional[threading.Thread]: The created audio thread, or None if mode is unknown.
    """
    if args.mode == "passthrough":
        return threading.Thread(
            target=audio_passthrough,
            args=(args.in_idx, args.out_idx, args.sr, args.in_ch, args.out_ch,
                  recorded_frames, vis_waveform_queue, audio_stop_event),
            kwargs={
                "save_recording": args.save_recording,
                "message_bus": message_bus
            }
        )
    elif args.mode == "record":
        return threading.Thread(
            target=audio_record,
            args=(args.in_idx, args.sr, args.in_ch,
                  recorded_frames, vis_waveform_queue, audio_stop_event),
            kwargs={
                "message_bus": message_bus
            }
        )
    elif args.mode == "playback":
        return threading.Thread(
            target=audio_playback,
            args=(args.out_idx, args.out_ch, args.wav_path, audio_stop_event, vis_waveform_queue),
            kwargs={
                "message_bus": message_bus
            }
        )
    else:
        logging.error(f"Unknown mode: {args.mode}")
        return None

def responsive_join(audio_thread: threading.Thread, vis_stop_event: Any, audio_stop_event: Any) -> None:
    """
    Join the audio thread, allowing for responsive shutdown.

    Parameters:
        audio_thread (threading.Thread): The audio processing thread.
        vis_stop_event (multiprocessing.Event): Event to signal visualizer shutdown.
        audio_stop_event (multiprocessing.Event): Event to signal audio shutdown.
    """
    try:
        while audio_thread.is_alive() and not vis_stop_event.is_set():
            audio_thread.join(timeout=0.1)
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received, stopping...")
        vis_stop_event.set()
        audio_stop_event.set()

def cleanup(
    vis_stop_event: Any,
    visualizer_proc: Any,
    audio_stop_event: Any,
    audio_thread: threading.Thread,
    vis_waveform_queue: Any,
    args: Any,
    recorded_frames: List[np.ndarray]
) -> None:
    """
    Clean up all resources and ensure proper shutdown of processes and threads.

    Parameters:
        vis_stop_event (multiprocessing.Event): Event to signal visualizer shutdown.
        visualizer_proc (Any): The visualizer process.
        audio_stop_event (multiprocessing.Event): Event to signal audio shutdown.
        audio_thread (threading.Thread): The audio processing thread.
        vis_waveform_queue (Any): Queue for waveform data.
        args (Any): The parsed command-line arguments.
        recorded_frames (List[np.ndarray]): List of recorded audio frames.
    """
    vis_stop_event.set()
    visualizer_proc.join(timeout=3)
    audio_stop_event.set()
    audio_thread.join(timeout=3)
    try:
        vis_waveform_queue.close()
        vis_waveform_queue.join_thread()
    except Exception as e:
        logging.debug(f"Error closing visualizer queue: {e}")
    if  "record" or (args.save_recording and args.mode == "passthrough"):
        save_recording(args.sr, recorded_frames)

def main() -> None:
    """
    Main entry point for the audio visualizer and recorder application.
    """
    # Ensure the global message queue is created in the main process
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    message_bus = MessageBus(queue)
    
    args = get_config()
    setup_logging(getattr(args, "log_level", "INFO"))

    logging.info(f"Using sample rate: {args.sr} Hz")
    logging.info(f"Input device: {args.in_idx}, Output device: {args.out_idx}")

    visualizer_sr = get_visualizer_sr(args)

    vis_stop_event = multiprocessing.Event()
    audio_stop_event = multiprocessing.Event()

    visualizer_proc, vis_waveform_queue = start_visualizer_process(
        sr=visualizer_sr,
        stop_event=vis_stop_event,
        waveform_queue=None,
        audio_stop_event=audio_stop_event,
        message_bus=message_bus
    )

    setup_signal_handlers(audio_stop_event, vis_stop_event)

    recorded_frames = []
    audio_thread = start_audio_thread(args, recorded_frames, vis_waveform_queue, audio_stop_event, message_bus)
    if audio_thread is None:
        return

    audio_thread.start()
    responsive_join(audio_thread, vis_stop_event, audio_stop_event)
    cleanup(
        vis_stop_event, visualizer_proc, audio_stop_event, audio_thread,
        vis_waveform_queue, args, recorded_frames
    )

if __name__ == '__main__':
    main()
    
