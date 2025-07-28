from pyqtgraph.Qt import QtWidgets
from visualizer.common_widgets.numeric_control import NumericControl
from message_bus import MessageBus, ReverbSettingsMessage
from visualizer.popup_widgets.popup_base import PopupBase

class ReverbPopup(PopupBase):
    def __init__(self, parent, message_bus: MessageBus):
        super().__init__(parent, message_bus)
        self.setWindowTitle("Reverb Settings")

        # Reverb delay samples
        self.reverb_samps_control = NumericControl(
            min_value=4000,
            max_value=44100,
            decimals=0,
            initial_value=16000,
            slider_steps=100,
            slider_change_func=self.reverb_event,
            input_change_func=self.reverb_event
        )
        self.layout.insertWidget(self.layout.count() - 2, QtWidgets.QLabel(self, text="Reverb Delay Samples"))
        self.layout.insertWidget(self.layout.count() - 2, self.reverb_samps_control)

        # Reverb decay
        self.reverb_decay_control = NumericControl(
            min_value=0.01,
            max_value=1.0,
            decimals=2,
            initial_value=0.9,
            slider_steps=100,
            slider_change_func=self.reverb_event,
            input_change_func=self.reverb_event
        )
        self.layout.insertWidget(self.layout.count() - 2, QtWidgets.QLabel(self, text="Reverb Decay"))
        self.layout.insertWidget(self.layout.count() - 2, self.reverb_decay_control)

        # Wet level
        self.reverb_wet_control = NumericControl(
            min_value=0.0,
            max_value=1.0,
            decimals=2,
            initial_value=0.5,
            slider_steps=100,
            slider_change_func=self.reverb_event,
            input_change_func=self.reverb_event
        )
        self.layout.insertWidget(self.layout.count() - 2, QtWidgets.QLabel(self, text="Wet Level"))
        self.layout.insertWidget(self.layout.count() - 2, self.reverb_wet_control)

        # Taps
        self.reverb_taps_control = NumericControl(
            min_value=1,
            max_value=25,
            decimals=0,
            initial_value=8,
            slider_steps=1,
            slider_change_func=self.reverb_event,
            input_change_func=self.reverb_event
        )
        self.layout.insertWidget(self.layout.count() - 2, QtWidgets.QLabel(self, text="Taps"))
        self.layout.insertWidget(self.layout.count() - 2, self.reverb_taps_control)

        # Reverb toggle button
        self.reverb_toggle_button = QtWidgets.QPushButton("Enable Reverb")
        self.reverb_toggle_button.setCheckable(True)
        self.reverb_toggle_button.toggled.connect(self.reverb_event)
        self.layout.insertWidget(self.layout.count() - 2, self.reverb_toggle_button)

        # Allow Clipping toggle button
        self.allow_clipping_button = QtWidgets.QPushButton("Allow Clipping")
        self.allow_clipping_button.setCheckable(True)
        self.allow_clipping_button.setChecked(True)
        self.allow_clipping_button.toggled.connect(self.reverb_event)
        self.layout.insertWidget(self.layout.count() - 2, self.allow_clipping_button)

    def reverb_event(self, _e=None):
        do_reverb = self.reverb_toggle_button.isChecked()
        decay = self.reverb_decay_control.get_value()
        samps = self.reverb_samps_control.get_value()
        wet = self.reverb_wet_control.get_value()
        taps = int(self.reverb_taps_control.get_value())
        allow_clipping = self.allow_clipping_button.isChecked()
        message = ReverbSettingsMessage(do_reverb, decay, samps, wet, taps, allow_clipping)
        if do_reverb:
            self.reverb_toggle_button.setText("Disable Reverb")
        else:
            self.reverb_toggle_button.setText("Enable Reverb")
        if allow_clipping:
            self.allow_clipping_button.setText("Disallow Clipping")
        else:
            self.allow_clipping_button.setText("Allow Clipping")
        if self.message_bus:
            self.message_bus.send(message)
