import multiprocessing
from queue import Empty
from typing import Optional

class Message:
    """
    Base class for all messages sent via the MessageBus.
    """
    type: str

class MessageBus:
    """
    Multiprocess-safe message bus for sending commands to the audio processing code.
    """
    def __init__(self, queue):
        self.queue = queue

    def send(self, message: "Message") -> None:
        self.queue.put(message)

    def receive(self, timeout: float = 0.01) -> Optional["Message"]:
        try:
            return self.queue.get(timeout=timeout)
        except Empty:
            return None

    def has_message(self) -> bool:
        return self.queue.qsize() > 0

class ReverbSettingsMessage(Message):
    """
    Message to enable or disable reverb and set its parameters.
    """
    type = "reverb_enable"

    def __init__(
        self,
        enabled: bool,
        decay: float,
        delay_samps: int,
        wet_level: float,
        taps: int,
        allow_clipping: bool
    ):
        self.enabled = enabled
        self.decay = decay
        self.delay_samps = delay_samps
        self.wet_level = wet_level
        self.taps = taps
        self.allow_clipping = allow_clipping

class AmplifierSettingsMessage(Message):
    """
    Message to set Amplifier parameters.
    """
    type = "amplifier_settings"

    def __init__(self, scale: float, enabled: bool, allow_clipping: bool):
        self.scale = scale
        self.enabled = enabled
        self.allow_clipping = allow_clipping
