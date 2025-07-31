from typing import Dict
from visualizer.popup_widgets.amplifier_popup import AmplifierPopup
from visualizer.popup_widgets.display_controls_popup import DisplayControlsPopup
from visualizer.popup_widgets.reverb_popup import ReverbPopup

ALL_POPUPS: Dict[str, type] = {
    "Amplifier": AmplifierPopup,
    "Display Controls": DisplayControlsPopup,
    "Reverb": ReverbPopup
}