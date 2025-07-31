from typing import Any, Dict

from pyqtgraph.Qt import QtWidgets  

from visualizer.popup_widgets.all_popups import ALL_POPUPS
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
        
        # Temp menu before plugin chains are added
        self.popups: Dict[str, Any] = {}
        for name, popup in ALL_POPUPS.items():
            
            def open_popup():
                if name not in self.popups.keys():
                    self.popups[name] = popup(self, message_bus=self.message_bus)
                self.popups[name].show()
                self.popups[name].raise_()
                self.popups[name].activateWindow()
            
            button = QtWidgets.QPushButton(name)
            button.clicked.connect(open_popup)
            main_layout.addWidget(button)
        

