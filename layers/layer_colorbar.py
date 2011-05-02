"""Defines a layer for drawing a colorbar based on some other layer's 
output."""

import matplotlib.colorbar
import matplotlayers.layer


class LayerColorbar(matplotlayers.layer.Layer):
    """This layer creates a matplotlib.colorbar.Colorbar in the axes
    it draws to.
    
    Since the axes are cleared when the LayerColorbar changes due to 
    changes of the mappable, there will be then a new Colorbar created.
    
    The layer must be registered to the layer providing the mappable by
    the 'layer_colorbar' configuration option of that layer."""

    def __init__(self, **kwargs):
        """All KWARGS go to the Colorbar constructor once it is created."""

        matplotlayers.layer.Layer.__init__(self)

        self.configure(**kwargs)

        self.mappable = None

    def set_mappable(self, mappable):
        """Sets the mappable (expected to be called by the providing layer),
        and sets the layer to changed."""

        self.configure(mappable=mappable)
        self.set_changed()

    def to_axes(self, axes):
        """Creates a new Colorbar in the AXES."""
    
        # When the layer has not yet provided a mappable, abort.
        if not self.is_configured('mappable'):
            return

        # self is also configured to hold the mappable.
        matplotlib.colorbar.Colorbar(ax=axes, **self)
