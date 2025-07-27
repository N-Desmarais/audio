import numpy as np
import queue
from typing import Any, Optional

from pyqtgraph.Qt import QtCore, QtWidgets  
from visualizer.layout import VisualizerLayout
from visualizer.spectrogram_graph import SpectrogramGraph
from visualizer.waveform_graph import WaveformGraph
from visualizer.numeric_control import NumericControl

class VisualizerGUI(QtWidgets.QWidget):
    """
    Main widget for the audio visualizer, containing waveform and spectrogram views and controls.
    """
    def __init__(
        self,
        samplerate: int,
        stop_event: Any,
        waveform_queue: Any,
        audio_stop_event: Optional[Any] = None,
        parent: Optional[Any] = None
    ) -> None:
        """
        Initialize the main visualizer GUI widget.

        Parameters:
            samplerate (int): The audio sample rate.
            stop_event (Any): Event to signal visualizer shutdown.
            waveform_queue (Any): Queue for passing waveform data.
            audio_stop_event (Optional[Any]): Event to signal audio shutdown.
            parent (Optional[Any]): The parent widget.
        """
        super().__init__(parent)
        self.samplerate = samplerate
        self.stop_event = stop_event
        self.audio_stop_event = audio_stop_event
        self.waveform_queue = waveform_queue

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        
        self.vis_layout = VisualizerLayout(parent=self)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addWidget(self.vis_layout)

        self.ymode = False
        self.buffer_seconds = 0.5
        self.plot_buffer = np.zeros(int(self.samplerate * self.buffer_seconds), dtype=np.float32)

        # Timers
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10)

        self.stop_timer = QtCore.QTimer()
        self.stop_timer.timeout.connect(self.check_stop)
        self.stop_timer.start(100)

    def update_buffer_size(self, new_seconds: float) -> None:
        """
        Change the buffer size for waveform and spectrogram displays.

        Parameters:
            new_seconds (float): The new buffer duration in seconds.
        """
        self.buffer_seconds = new_seconds
        self.plot_buffer = np.zeros(int(self.samplerate * self.buffer_seconds), dtype=np.float32)
        self.vis_layout.waveform_graph.set_xrange(0, self.buffer_seconds)
        self.vis_layout.spectrogram_graph.spectrogram_plot.setXRange(0, self.buffer_seconds, padding=0)

    def update(self) -> None:
        """
        Refresh the waveform and spectrogram displays with new data.
        """
        updated = False
        chunk = None
        try:
            chunk = self.waveform_queue.get_nowait()
            if chunk.size != 0:
                n = len(chunk)
                if n > len(self.plot_buffer):
                    chunk = chunk[-len(self.plot_buffer):]
                    n = len(chunk)
                self.plot_buffer[:-n] = self.plot_buffer[n:]
                self.plot_buffer[-n:] = chunk
                updated = True
        except queue.Empty:
            pass
        if updated:
            self.vis_layout.waveform_graph.update(self.ymode, self.buffer_seconds, self.plot_buffer)
            self.vis_layout.spectrogram_graph.update(chunk, self.buffer_seconds, self.samplerate)

    def check_stop(self) -> None:
        """
        Check if the stop event is set and close the widget if so.
        """
        if self.stop_event.is_set():
            self.close()

    def on_close(self) -> None:
        """
        Handle the exit button or window close event by signaling shutdown.
        """
        self.stop_event.set()
        if self.audio_stop_event is not None:
            self.audio_stop_event.set()
        QtCore.QCoreApplication.quit()

    def closeEvent(self, event: Any) -> None:
        """
        Ensure all threads and processes are stopped when the window closes.

        Parameters:
            event (Any): The close event.
        """
        self.on_close()
        event.accept()

    def mousePressEvent(self, event: Any) -> None:
        """
        Handle mouse press events to enable window dragging.

        Parameters:
            event (Any): The mouse event.
        """
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: Any) -> None:
        """
        Handle mouse move events for window dragging.

        Parameters:
            event (Any): The mouse event.
        """
        if event.buttons() & QtCore.Qt.LeftButton:
            if hasattr(self, "_drag_pos"):
                self.move(event.globalPos() - self._drag_pos)
            event.accept()

