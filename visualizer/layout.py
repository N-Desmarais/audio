from PyQt5.QtCore import Qt
from pyqtgraph.Qt import QtCore, QtWidgets  

from visualizer.spectrogram_graph import SpectrogramGraph
from visualizer.waveform_graph import WaveformGraph
from visualizer.control_panel import ControlPanel

class VisualizerLayout(QtWidgets.QWidget):
    """
    Widget that arranges the visualizer's tabs and control panel.
    """
    def __init__(
        self,
        parent: QtWidgets.QWidget
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
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Waveform & Sprectrogram tabs
        self.waveform_graph = WaveformGraph(pen='c')
        self.spectrogram_graph = SpectrogramGraph()
        self.tabs.addTab(self.waveform_graph.plot_widget, "Waveform")
        self.tabs.addTab(self.spectrogram_graph.spectrogram_tab, "Spectrogram")
        layout.addWidget(self.tabs, stretch=1)  # Tabs take all available space

        # Control panel (fixed width, right side)
        self.control_panel = ControlPanel(state=parent, parent=self)
        self.control_panel.setFixedWidth(220)  # Adjust width as needed
        layout.addWidget(self.control_panel)   # No stretch, stays to the right
        
    def on_tab_changed(self, idx: int) -> None:
        """
        Show or hide controls depending on the selected tab.

        Parameters:
            idx (int): The index of the selected tab.
        """
        
        if not hasattr(self, "control_panel"):
            return
        
        tab_text = self.tabs.tabText(idx)
        if tab_text == "Spectrogram":
            self.control_panel.y_mode_button.hide()
            self.control_panel.spectrogram_cmap_label.setVisible(True)
            self.control_panel.spectrogram_cmap_dropdown.setVisible(True)
        else:
            self.control_panel.y_mode_button.show()
            self.control_panel.spectrogram_cmap_label.setVisible(False)
            self.control_panel.spectrogram_cmap_dropdown.setVisible(False)