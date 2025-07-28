from pyqtgraph.Qt import QtWidgets
from visualizer.common_widgets.numeric_control import NumericControl
from visualizer.popup_widgets.popup_base import PopupBase

COLOR_MAPS = [
    'thermal', 'flame', 'yellowy', 'bipolar', 'spectrum', 'cyclic', 'greyclip', 'grey', 'viridis', 'inferno', 'plasma', 'magma', 'turbo'
]

BRIGHT_PENS = [
    ('Cyan', 'c'),
    ('Magenta', 'm'),
    ('Yellow', 'y'),
    ('Red', 'r'),
    ('Green', 'g'),
    ('Blue', 'b'),
    ('White', 'w')
]

class DisplayControlsPopup(PopupBase):
    def __init__(
        self,
        parent,
        gui
    ):
        super().__init__(parent, message_bus=None)
        self.setWindowTitle("Display Controls")
        self.gui = gui
        self.waveform_graph = self.gui.vis_layout.waveform_graph
        self.spectrogram_graph = self.gui.vis_layout.spectrogram_graph
        
        
        self.y_mode_button = QtWidgets.QPushButton("Show Decibels")
        self.y_mode_button.setCheckable(True)
        self.y_mode_button.setChecked(self.waveform_graph.ymode)
        self.y_mode_button.toggled.connect(self.on_y_mode_toggle)
        self.layout.insertWidget(self.layout.count() - 2, self.y_mode_button)

        # Area under curve toggle
        self.area_button = QtWidgets.QPushButton("Show Area Under Curve")
        self.area_button.setCheckable(True)
        self.area_button.setChecked(False)
        self.area_button.toggled.connect(self.on_area_toggle)
        self.layout.insertWidget(self.layout.count() - 2, self.area_button)

        # Spectrogram Color Map Dropdown
        self.spectrogram_cmap_label = QtWidgets.QLabel("Spectrogram Color Scale:")
        self.spectrogram_cmap_dropdown = QtWidgets.QComboBox()
        self.spectrogram_cmap_dropdown.addItems(COLOR_MAPS)
        self.spectrogram_cmap_dropdown.setCurrentText('viridis')
        self.spectrogram_cmap_dropdown.setToolTip("Spectrogram Color Scale")
        self.spectrogram_cmap_dropdown.currentTextChanged.connect(
            self.spectrogram_graph.spectrogram_colorbar.gradient.loadPreset
        )
        self.layout.insertWidget(self.layout.count() - 2, self.spectrogram_cmap_label)
        self.layout.insertWidget(self.layout.count() - 2, self.spectrogram_cmap_dropdown)

        # Waveform Pen Color Dropdown
        self.waveform_pen_label = QtWidgets.QLabel("Waveform Color:")
        self.waveform_pen_dropdown = QtWidgets.QComboBox()
        for name, pen in BRIGHT_PENS:
            self.waveform_pen_dropdown.addItem(name, pen)
        # Set current to match waveform's pen if possible
        current_pen = getattr(self.waveform_graph.curve.opts, 'pen', 'c')
        idx = [p for _, p in BRIGHT_PENS].index('c') if 'c' in [p for _, p in BRIGHT_PENS] else 0
        self.waveform_pen_dropdown.setCurrentIndex(idx)
        self.waveform_pen_dropdown.currentIndexChanged.connect(self.on_waveform_pen_changed)
        self.layout.insertWidget(self.layout.count() - 2, self.waveform_pen_label)
        self.layout.insertWidget(self.layout.count() - 2, self.waveform_pen_dropdown)

        # Window duration Slider
        self.duration_control = NumericControl(
            min_value=0.01,
            max_value=10.0,
            decimals=2,
            initial_value=5.0,
            slider_steps=100,
            slider_change_func=self.gui.update_buffer_size,
            input_change_func=self.gui.update_buffer_size
        )
        self.layout.insertWidget(self.layout.count() - 2, QtWidgets.QLabel(self, text="Window Duration"))
        self.layout.insertWidget(self.layout.count() - 2, self.duration_control)
        
    def on_y_mode_toggle(self) -> None:
        """
        Toggle between amplitude and decibel display modes for the waveform.
        """
        
        self.waveform_graph.ymode = not self.waveform_graph.ymode  
        
        if self.waveform_graph.ymode:
            self.waveform_graph.set_ylabel('Level (dB)')
            self.waveform_graph.set_yrange(-80, 0)
            self.y_mode_button.setText("Show Amplitube")
        else:
            self.waveform_graph.set_ylabel('Amplitude')
            self.waveform_graph.set_yrange(-1.0, 1.0)
            self.y_mode_button.setText("Show Decibels")

    def on_area_toggle(self, checked: bool) -> None:
        """
        Toggle area under curve display on the waveform graph.
        """
        self.waveform_graph.toggle_area_enabled(checked)
        text = "Show Area Under Curve" if not checked else "Hide Area Under Curve"
        self.area_button.setText(text)

    def on_waveform_pen_changed(self, idx: int) -> None:
        """
        Change the waveform plot pen color.
        """
        pen = self.waveform_pen_dropdown.itemData(idx)
        self.waveform_graph.set_pen(pen)

