<!-- Project image -->
<p align="center">
  <img src="images/example.png" alt="Audio Visualizer" width="500"/>
</p>

# Audio Visualizer & Recorder

This project is a Python-based suite for practicing Digital Signal Processing (DSP) concepts. It provides real-time audio visualization, recording, playback, and passthrough, with a PyQt5/pyqtgraph GUI for waveform and spectrogram display.

## Architecture

- **audio_processing.py:** Audio I/O and processing functions.
- **visualizer/**: GUI code for visualization.
- **arg_parser.py:** Command-line argument parsing.
- **file_utils.py:** Utilities for saving audio.

### IPC

- **Multiprocessing.Queue:** Sends waveform data from audio thread to GUI.
- **Multiprocessing.Event:** Signals shutdown between processes/threads.

## Usage

```sh
python main.py --mode passthrough --input_device 1 --output_device 3
python main.py --mode playback --output_device 3 --wav_path recordings/example.wav
```