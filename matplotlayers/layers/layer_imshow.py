import matplotlayers.layer
import keyconf

"""Showing some image."""


class LayerImshow(matplotlayers.layer.Layer):
    """Plotting some image."""

    def __init__(self, **kwargs):
        """All arguments go to axes.imshow."""

        matplotlayers.layer.Layer.__init__(self)
    
        self.configure(**kwargs)

    def to_axes(self, axes):
        """Shows the image."""

        if not self.is_configured('X'):
            return

        axes.imshow(**self)
