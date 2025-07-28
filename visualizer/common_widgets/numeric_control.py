from typing import Any, Callable, Optional

from pyqtgraph.Qt import QtCore, QtGui, QtWidgets  


class NumericControl(QtWidgets.QWidget):
    """
    Numeric control widget with a line edit and slider for adjusting a value.
    """

    def __init__(
        self,
        min_value: float = 0.0,
        max_value: float = 1.0,
        decimals: int = 2,
        initial_value: float = 0.5,
        slider_steps: int = 100,
        parent: Optional[Any] = None,
        slider_change_func: Callable[[float], None] = lambda x: None,
        input_change_func: Callable[[float], None] = lambda x: None,
    ) -> None:
        """
        Initialize the numeric control widget.

        Parameters:
            min_value (float): The minimum allowed value.
            max_value (float): The maximum allowed value.
            decimals (int): Number of decimal places to display.
            initial_value (float): The initial value to set.
            slider_steps (int): Number of steps for the slider.
            parent (Optional[Any]): The parent widget.
            slider_change_func (Callable[[float], None]): Callback for slider changes.
            input_change_func (Callable[[float], None]): Callback for input changes.
        """
        super().__init__(parent)
        self.layout = QtWidgets.QHBoxLayout(self)

        self.input = QtWidgets.QLineEdit(f"{initial_value:.{decimals}f}")
        self.input.setValidator(QtGui.QDoubleValidator(min_value, max_value, decimals))
        self.input.setMaximumWidth(50)
        self.layout.addWidget(self.input)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(int(min_value * slider_steps))
        self.slider.setMaximum(int(max_value * slider_steps))
        self.slider.setValue(int(initial_value * slider_steps))
        self.layout.addWidget(self.slider)

        self.decimals = decimals
        self.slider_steps = slider_steps
        self.min_value = min_value
        self.max_value = max_value

        self.slider_change_func = slider_change_func
        self.input_change_func = input_change_func

        self.slider.valueChanged.connect(self._on_slider_change)
        self.input.editingFinished.connect(self._on_input_change)

    def get_value(self) -> float:
        """
        Get the current value from the slider.

        Returns:
            float: The current value.
        """
        return self.slider.value() / self.slider_steps

    def set_value(self, value: float) -> None:
        """
        Set the value for both the slider and input field.

        Parameters:
            value (float): The value to set.
        """
        value = max(self.min_value, min(self.max_value, value))
        self.slider.setValue(int(value * self.slider_steps))
        self.input.setText(f"{value:.{self.decimals}f}")

    def _on_slider_change(self) -> None:
        """
        Handle changes to the slider value and update the input field.
        """
        value = self.get_value()
        self.input.setText(f"{value:.{self.decimals}f}")
        self.slider_change_func(value)

    def _on_input_change(self) -> None:
        """
        Handle changes to the input field and update the slider.
        """
        try:
            value = float(self.input.text())
            self.set_value(value)
            self.input_change_func(value)
        except ValueError:
            pass