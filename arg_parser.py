import argparse
from typing import Optional, Tuple

import sounddevice as sd  

def list_devices(kind: str = 'input') -> None:
    """
    Print a list of available audio devices of the specified kind.

    Parameters:
        kind (str): Either 'input' or 'output' to specify device type.
    """
    print(f"\nAvailable {kind} devices:")
    for i, dev in enumerate(sd.query_devices()):
        if (kind == 'input' and dev['max_input_channels'] > 0) or \
           (kind == 'output' and dev['max_output_channels'] > 0):
            print(f"{i}: {dev['name']} ({dev['default_samplerate']} Hz)")

def select_device(idx: Optional[int] = None, kind: str = 'input') -> Tuple[int, int, int]:
    """
    Select an audio device by index or prompt the user to choose one.

    Parameters:
        idx (Optional[int]): The device index. If None, prompt the user.
        kind (str): Either 'input' or 'output' to specify device type.

    Returns:
        Tuple[int, int, int]: The device index, channel count, and sample rate.
    """
    if idx is None:
        list_devices(kind)
        idx = int(input(f"Select {kind} device index: "))
    info = sd.query_devices(idx)
    ch = info['max_input_channels'] if kind == 'input' else info['max_output_channels']
    sr = int(info['default_samplerate'])
    return idx, ch, sr

def get_config() -> argparse.Namespace:
    """
    Parse command-line arguments and return the configuration.

    Returns:
        argparse.Namespace: The parsed arguments with additional device info.
    """
    parser = argparse.ArgumentParser(description="Audio loopback recorder")
    parser.add_argument('--input_device', type=int, default=None,
                        help='Input device index (default: prompt)')
    parser.add_argument('--output_device', type=int, default=None,
                        help='Output device index (default: prompt)')
    parser.add_argument('--wav_path', type=str, default=None,
                        help='Path to WAV file for playback mode')
    parser.add_argument('--list_devices', action='store_true',
                        help='List available audio devices and exit')
    parser.add_argument('--mode', type=str, choices=['playback', 'record', 'passthrough'],
                        default='passthrough', help="Operation mode: playback, record, or passthrough (default: passthrough)")
    parser.add_argument('--log_level', type=str, default='INFO',
                        help='Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument("--save_recording", action="store_true", help="Save recording in passthrough/record mode")
    parser.add_argument('--in_ch', type=int, default=None,
                        help='Number of channels to use for input (default: device max)')
    parser.add_argument('--out_ch', type=int, default=None,
                        help='Number of channels to use for output (default: device max)')
    args = parser.parse_args()

    if args.list_devices:
        list_devices('input')
        list_devices('output')
        exit(0)

    # Device selection logic based on mode
    in_idx: int | None = None
    in_ch: int | None = None
    out_idx: int | None = None
    out_ch: int | None = None
    sr: int | None = None

    if args.mode in ('record', 'passthrough'):
        in_idx, in_ch, sr = select_device(args.input_device, 'input')
    if args.mode in ('playback', 'passthrough'):
        out_idx, out_ch, sr = select_device(args.output_device, 'output')

    args.in_idx = in_idx
    args.in_ch = args.in_ch or in_ch
    args.out_idx = out_idx
    args.out_ch = args.out_ch or out_ch
    args.sr = sr
    return args