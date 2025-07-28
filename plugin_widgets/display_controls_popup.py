from pyqtgraph.Qt import QtWidgets
from visualizer.common_widgets.numeric_control import NumericControl
from visualizer.plugin_widgets.popup_base import PopupBase

COLOR_MAPS = [
    'thermal', 'flame', 'yellowy', 'bipolar', 'spectrum', 'cyclic', 'greyclip', 'grey', 'viridis', 'inferno', 'plasma', 'magma', 'turbo'
]

class DisplayControlsPopup(PopupBase):
    def __init__(
        self,
        parent,
        layout
    ):
        super().__init__(parent, message_bus=None)
        self.setWindowTitle("Display Controls")
        self.layout_obj = layout

        # Y mode toggle
        self.y_mode_button = QtWidgets.QPushButton(
            "Show Decibels" if not self.layout_obj.parent.ymode else "Show Amplitude"
        )
        self.y_mode_button.setCheckable(True)
        self.y_mode_button.setChecked(self.layout_obj.parent.ymode)
        self.y_mode_button.toggled.connect(self.layout_obj.on_y_mode_toggle)
        self.layout.insertWidget(self.layout.count() - 2, self.y_mode_button)

        # Spectrogram Color Map Dropdown
        self.spectrogram_cmap_label = QtWidgets.QLabel("Spectrogram Color Scale:")
        self.spectrogram_cmap_dropdown = QtWidgets.QComboBox()
        self.spectrogram_cmap_dropdown.addItems(COLOR_MAPS)
        self.spectrogram_cmap_dropdown.setCurrentText('viridis')
        self.spectrogram_cmap_dropdown.setToolTip("Spectrogram Color Scale")
        self.spectrogram_cmap_dropdown.currentTextChanged.connect(
            self.layout_obj.vis_layout.spectrogram_graph.spectrogram_colorbar.gradient.loadPreset
        )
        self.layout.insertWidget(self.layout.count() - 2, self.spectrogram_cmap_label)
        self.layout.insertWidget(self.layout.count() - 2, self.spectrogram_cmap_dropdown)

        # Window duration Slider
        self.duration_control = NumericControl(
            min_value=0.01,
            max_value=10.0,
            decimals=2,
            initial_value=5.0,
            slider_steps=100,
            slider_change_func=self.layout_obj.update_buffer_size,
            input_change_func=self.layout_obj.update_buffer_size
        )
        self.layout.insertWidget(self.layout.count() - 2, QtWidgets.QLabel(self, text="Window Duration"))
        self.layout.insertWidget(self.layout.count() - 2, self.duration_control)
