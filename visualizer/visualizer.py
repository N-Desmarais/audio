from multiprocessing import Event, Process, Queue
from typing import Any, Optional, Tuple

from PyQt5.QtCore import QFile, QIODevice, QTextStream
from pyqtgraph.Qt import QtWidgets  

from visualizer.visualizer_widget import VisualizerGUI

class VisualizerApp:
    """
    Application class for running the audio visualizer GUI.
    """
    def __init__(
        self,
        sr: int,
        stop_event: Any,
        waveform_queue: Queue,
        audio_stop_event: Optional[Any] = None
    ) -> None:
        """
        Initialize the VisualizerApp.

        Parameters:
            sr (int): Sample rate.
            stop_event (Any): Event to signal visualizer shutdown.
            waveform_queue (Queue): Queue for waveform data.
            audio_stop_event (Optional[Any]): Event to signal audio shutdown.
        """
        self.app = QtWidgets.QApplication([])
        self.load_global_styles()
        self.widget = VisualizerGUI(sr, stop_event, waveform_queue, audio_stop_event)
        self.widget.setWindowTitle("Live Audio Visualizer")
        self.widget.show()
        self.widget.raise_()  # Bring window to front
        self.widget.activateWindow()  # Focus the window

    def exec(self) -> None:
        """
        Start the Qt event loop.
        """
        self.app.exec()
        
    def load_global_styles(self) -> None:
        """
        Load global stylesheet for the application.
        """
        stylesheet_path = r'visualizer\style.qss'
        with open(stylesheet_path,"r") as fh:
            self.app.setStyleSheet(fh.read())

def visualizer_process_with_ready(
    sr: int,
    stop_event: Any,
    waveform_queue: Queue,
    audio_stop_event: Optional[Any],
    window_ready: Any
) -> None:
    """
    Run the visualizer process and signal when the window is ready.

    Parameters:
        sr (int): Sample rate.
        stop_event (Any): Event to signal visualizer shutdown.
        waveform_queue (Queue): Queue for waveform data.
        audio_stop_event (Optional[Any]): Event to signal audio shutdown.
        window_ready (Any): Event to signal when the window is ready.
    """
    app = VisualizerApp(sr, stop_event, waveform_queue, audio_stop_event)
    app.widget.show()
    app.widget.raise_()
    app.widget.activateWindow()
    window_ready.set()
    app.exec()

def start_visualizer_process(
    sr: int,
    stop_event: Optional[Any] = None,
    waveform_queue: Optional[Queue] = None,
    audio_stop_event: Optional[Any] = None
) -> Tuple[Process, Queue]:
    """
    Start the visualizer process in a separate process.

    Parameters:
        sr (int): Sample rate.
        stop_event (Optional[Any]): Event to signal visualizer shutdown.
        waveform_queue (Optional[Queue]): Queue for waveform data.
        audio_stop_event (Optional[Any]): Event to signal audio shutdown.

    Returns:
        Tuple[Process, Queue]: The process and waveform queue.
    """
    if stop_event is None:
        stop_event = Event()
    if waveform_queue is None:
        waveform_queue = Queue()

    from multiprocessing import Event as MpEvent
    window_ready = MpEvent()

    p = Process(
        target=visualizer_process_with_ready,
        args=(sr, stop_event, waveform_queue, audio_stop_event, window_ready)
    )
    p.start()

    # Wait for the window to be shown (or timeout)
    window_ready.wait(timeout=5)
    return p, waveform_queue
