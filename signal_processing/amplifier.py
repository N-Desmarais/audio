class AmplifierPlugin:
    def __init__(self, scale: float = 1.0, allow_clipping: bool = True):
        self.scale = scale
        self.allow_clipping = allow_clipping

    def apply(self, input_signal):
        output = input_signal * self.scale
        if not self.allow_clipping:
            max_val = max(1.0, abs(output).max())
            output = output / max_val
        return output

    def set_scale(self, scale: float):
        self.scale = scale

    def set_enabled(self, enabled: bool):
        self.enabled = enabled

    def set_allow_clipping(self, allow_clipping: bool):
        self.allow_clipping = allow_clipping

    def reset(self):
        self.scale = 1.0
        self.enabled = True
        self.allow_clipping = True
