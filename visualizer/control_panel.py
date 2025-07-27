from typing import Any

from pyqtgraph.Qt import QtWidgets  

from visualizer.numeric_control import NumericControl

COLOR_MAPS = [
    'thermal', 'flame', 'yellowy', 'bipolar', 'spectrum', 'cyclic', 'greyclip', 'grey', 'viridis', 'inferno', 'plasma', 'magma', 'turbo'
]

class ControlPanel(QtWidgets.QWidget):
    def __init__(self, state: Any, parent: Any = None) -> None:
        """
        Initialize the control panel widget with controls for the visualizer.

        Parameters:
            state (Any): The state object for callbacks.
            parent (Any): The parent widget.
        """
        super().__init__(parent)

        # Main layout for the control panel
        main_layout = QtWidgets.QVBoxLayout(self)

        # Exit button row
        self.exit_button = QtWidgets.QPushButton("Exit")
        self.exit_button.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        self.exit_button.clicked.connect(state.on_close)
        exit_row = QtWidgets.QHBoxLayout()
        exit_row.addStretch(1)
        exit_row.addWidget(self.exit_button)
        main_layout.addLayout(exit_row)
        main_layout.addStretch(1)

        # Amplitude / dB toggle button
        self.y_mode_button = QtWidgets.QPushButton("Show Decibels")
        self.y_mode_button.setCheckable(True)
        self.y_mode_button.toggled.connect(self.on_y_mode_toggle)
        main_layout.addWidget(self.y_mode_button)

        # Spectrogram Color Map Dropdown
        callback = parent.spectrogram_graph.spectrogram_colorbar.gradient.loadPreset            
        self.spectrogram_cmap_label = QtWidgets.QLabel("Spectrogram Color Scale:")
        self.spectrogram_cmap_label.setVisible(False)
        self.spectrogram_cmap_dropdown = QtWidgets.QComboBox()
        self.spectrogram_cmap_dropdown.addItems(COLOR_MAPS)
        self.spectrogram_cmap_dropdown.setCurrentText('viridis')
        self.spectrogram_cmap_dropdown.setVisible(False)
        self.spectrogram_cmap_dropdown.setToolTip("Spectrogram Color Scale")
        self.spectrogram_cmap_dropdown.currentTextChanged.connect(callback)
        
        main_layout.addWidget(self.spectrogram_cmap_label)
        main_layout.addWidget(self.spectrogram_cmap_dropdown)
        
        # Window duration Slider
        self.duration_control = NumericControl(
            min_value=0.01,
            max_value=10.0,
            decimals=2,
            initial_value=5.0,
            slider_steps=100,
            slider_change_func=state.update_buffer_size,
            input_change_func=state.update_buffer_size
        )
        main_layout.addWidget(QtWidgets.QLabel(self, text="Window Duration"))
        main_layout.addWidget(self.duration_control)

    def on_y_mode_toggle(self) -> None:
        """
        Toggle between amplitude and decibel display modes for the waveform.
        """
        db_mode = self.y_mode_button.isChecked()
        parent = self.parent()
        parent.ymode = db_mode
        if db_mode:
            self.y_mode_button.setText("Show Amplitude")
            parent.waveform_graph.set_ylabel('Level (dB)')
            parent.waveform_graph.set_yrange(-80, 0)
        else:
            self.y_mode_button.setText("Show Decibels")
            parent.waveform_graph.set_ylabel('Amplitude')
            parent.waveform_graph.set_yrange(-1.0, 1.0)