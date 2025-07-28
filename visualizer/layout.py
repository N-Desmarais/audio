from PyQt5.QtCore import Qt
from pyqtgraph.Qt import QtCore, QtWidgets  

from message_bus import MessageBus
from visualizer.graphing_widgets.spectrogram_graph import SpectrogramGraph
from visualizer.graphing_widgets.waveform_graph import WaveformGraph
from visualizer.control_panel import ControlPanel

class VisualizerLayout(QtWidgets.QWidget):
    """
    Widget that arranges the visualizer's tabs and control panel.
    """
    def __init__(
        self,
        parent: QtWidgets.QWidget,
        message_bus: MessageBus
    ) -> None:
        """
        Initialize the VisualizerLayout widget.

        Parameters:
            parent (QtWidgets.QWidget): The parent widget.
        """
        super().__init__(parent)
        # Use a QHBoxLayout as the internal layout
        layout = QtWidgets.QHBoxLayout(self)
        self.closeEvent = lambda ev: (parent.on_close(), ev.accept())

        # --- Tabs for waveform and spectrogram ---
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabs.setStyleSheet("QTabBar::tab { height: 24px; width: 120px; }")

        # Waveform & Sprectrogram tabs
        self.waveform_graph = WaveformGraph(pen='c')
        self.spectrogram_graph = SpectrogramGraph()
        self.tabs.addTab(self.waveform_graph.plot_widget, "Waveform")
        self.tabs.addTab(self.spectrogram_graph.spectrogram_tab, "Spectrogram")
        layout.addWidget(self.tabs, stretch=1)  # Tabs take all available space

        # Control panel (fixed width, right side)
        self.control_panel = ControlPanel(state=parent, parent=self, message_bus=message_bus)
        self.control_panel.setFixedWidth(220)  # Adjust width as needed
        layout.addWidget(self.control_panel)   # No stretch, stays to the right
        
        # No-op: controls are now in popup
        pass