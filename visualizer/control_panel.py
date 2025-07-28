from typing import Any

from pyqtgraph.Qt import QtWidgets  

from visualizer.popup_widgets.reverb_popup import ReverbPopup
from visualizer.popup_widgets.display_controls_popup import DisplayControlsPopup
from visualizer.popup_widgets.amplifier_popup import AmplifierPopup
from message_bus import MessageBus

class ControlPanel(QtWidgets.QWidget):
    def __init__(self, state: Any, parent: Any = None, message_bus: MessageBus = None) -> None:
        """
        Initialize the control panel widget with controls for the visualizer.

        Parameters:
            state (Any): The state object for callbacks.
            parent (Any): The parent widget.
        """
        super().__init__(parent)
        
        self.message_bus = message_bus

        # Main layout for the control panel
        main_layout = QtWidgets.QVBoxLayout(self)

        # Exit button row
        self.exit_button = QtWidgets.QPushButton("Exit")
        self.exit_button.setObjectName("EXIT")
        self.exit_button.clicked.connect(state.on_close)
        exit_row = QtWidgets.QHBoxLayout()
        exit_row.addStretch(1)
        exit_row.addWidget(self.exit_button)
        main_layout.addLayout(exit_row)
        main_layout.addStretch(1)
        
        # --- Display Controls Button (opens popup) ---
        self.display_controls_button = QtWidgets.QPushButton("Display Controls")
        self.display_controls_button.clicked.connect(self.open_display_controls_popup)
        main_layout.addWidget(self.display_controls_button)

        # --- Reverb Button (opens popup) ---
        self.reverb_button = QtWidgets.QPushButton("Reverb")
        self.reverb_button.clicked.connect(self.open_reverb_popup)
        main_layout.addWidget(self.reverb_button)

        # --- Reverb popup instance ---
        self.reverb_popup = None
        self.display_controls_popup = None
        self.amplifier_popup = None

        # --- Amplifier Button (opens popup) ---
        self.amplifier_button = QtWidgets.QPushButton("Amplifier")
        self.amplifier_button.clicked.connect(self.open_amplifier_popup)
        main_layout.addWidget(self.amplifier_button)

    def open_reverb_popup(self):
        if self.reverb_popup is None:
            self.reverb_popup = ReverbPopup(self, message_bus=self.message_bus)
        self.reverb_popup.show()
        self.reverb_popup.raise_()
        self.reverb_popup.activateWindow()

    def open_display_controls_popup(self):
        if self.display_controls_popup is None:
            self.display_controls_popup = DisplayControlsPopup(
                parent=self,
                gui=self.parent().parent()
            )
        self.display_controls_popup.show()
        self.display_controls_popup.raise_()
        self.display_controls_popup.activateWindow()

    def open_amplifier_popup(self):
        if self.amplifier_popup is None:
            self.amplifier_popup = AmplifierPopup(self, message_bus=self.message_bus)
        self.amplifier_popup.show()
        self.amplifier_popup.raise_()
        self.amplifier_popup.activateWindow()