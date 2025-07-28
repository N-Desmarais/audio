from pyqtgraph.Qt import QtWidgets, QtCore
from message_bus import MessageBus

class PopupBase(QtWidgets.QDialog): 
    def __init__(self, parent, message_bus: MessageBus):
        super().__init__(parent)
        self.setWindowFlags(
            self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint
        )
        self.message_bus = message_bus
        self.layout = QtWidgets.QVBoxLayout(self)
        self._drag_active = False
        self._drag_position = None

        # Close button at the bottom
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.close)
        self.layout.addStretch(1)
        self.layout.addWidget(close_btn)

    # --- Mouse event handlers for dragging ---
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_active = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_active = False
            event.accept()
        super().mouseReleaseEvent(event)
