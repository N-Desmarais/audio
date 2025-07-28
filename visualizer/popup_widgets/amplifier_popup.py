from pyqtgraph.Qt import QtWidgets
from visualizer.common_widgets.numeric_control import NumericControl
from message_bus import MessageBus, AmplifierSettingsMessage
from visualizer.popup_widgets.popup_base import PopupBase

class AmplifierPopup(PopupBase):
    def __init__(self, parent, message_bus: MessageBus):
        super().__init__(parent, message_bus)
        self.setWindowTitle("Amplifier Settings")

        # Amplifier scale control
        self.scale_control = NumericControl(
            min_value=.01,
            max_value=10.0,
            decimals=2,
            initial_value=1.0,
            slider_steps=1000,
            slider_change_func=self.amplifier_event,
            input_change_func=self.amplifier_event
        )
        self.layout.insertWidget(self.layout.count() - 2, QtWidgets.QLabel(self, text="Amplifier Scale"))
        self.layout.insertWidget(self.layout.count() - 2, self.scale_control)

        # Enable/Disable toggle
        self.enable_button = QtWidgets.QPushButton("Enable Amplifier")
        self.enable_button.setCheckable(True)
        self.enable_button.setChecked(True)
        self.enable_button.toggled.connect(self.amplifier_event)
        self.layout.insertWidget(self.layout.count() - 2, self.enable_button)

        # Allow/Disallow Clipping toggle
        self.allow_clipping_button = QtWidgets.QPushButton("Allow Clipping")
        self.allow_clipping_button.setCheckable(True)
        self.allow_clipping_button.setChecked(True)
        self.allow_clipping_button.toggled.connect(self.amplifier_event)
        self.layout.insertWidget(self.layout.count() - 2, self.allow_clipping_button)

    def amplifier_event(self, _e=None):
        scale = self.scale_control.get_value()
        enabled = self.enable_button.isChecked()
        allow_clipping = self.allow_clipping_button.isChecked()
        if enabled:
            self.enable_button.setText("Disable Amplifier")
        else:
            self.enable_button.setText("Enable Amplifier")
        if allow_clipping:
            self.allow_clipping_button.setText("Disallow Clipping")
        else:
            self.allow_clipping_button.setText("Allow Clipping")
        message = AmplifierSettingsMessage(scale, enabled, allow_clipping)
        if self.message_bus:
            self.message_bus.send(message)
