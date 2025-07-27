import logging
from pathlib import Path
from typing import List

import numpy as np
from scipy.io.wavfile import write

def save_recording(sr: int, recorded_frames: List[np.ndarray]) -> None:
    """
    Save the recorded audio frames to a WAV file on disk.

    Parameters:
        sr (int): The sample rate of the audio.
        recorded_frames (List[np.ndarray]): List of numpy arrays containing audio data.

    Returns:
        None
    """
    if not recorded_frames:
        logging.info("No audio recorded.")
        return

    recordings_dir = Path(__file__).parent / "recordings"
    recordings_dir.mkdir(exist_ok=True)

    existing = [
        fname for fname in recordings_dir.iterdir()
        if fname.name.startswith("recording") and fname.name.endswith(".wav")
    ]
    nums = []
    for fname in existing:
        try:
            num = int(fname.name[len("recording"):-4])
            nums.append(num)
        except ValueError:
            continue
    next_num = max(nums, default=0) + 1

    filename = recordings_dir / f"recording{next_num}.wav"

    audio = np.concatenate(recorded_frames, axis=0)
    audio_int16 = np.int16(audio * 32767)
    write(filename, sr, audio_int16)
    logging.info(f"Saved recording to {filename}")