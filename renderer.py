# Copyright (c) 2008, 2009, 2010 Friedrich Romstedt 
# <www.friedrichromstedt.org>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Developed since: Jul 2008

import matplotlib_backend_fr
import matplotlayers.layers

class Renderer:
    """Renders layers to a matplotlib_backend_fr.FigureAxes instance."""

    def __init__(self, figure_axes = None):
        """Connect to matplotlib_backend_fr.FigureAxes instance 
        FIGURE_AXES, if not given, create a new one without 
        arguments."""

        if figure_axes is None:
            # This creates also a new figure inside of the 
            # FigureAxes:
            figure_axes = matplotlib_backends_fr.FigureAxes()

        # Initialise attributes ...

        self.figure_axes = figure_axes

        # The layers present.
        self._layers = []
        
        # The layers rendered to the FigureAxes.
        self._layers_drawn = []

        # Whether a reset of the FigureAxes is needed before rendering.  This
        # may occur because:
        #  1.  Layers drawn have changed data.
        #  2.  Layers have been removed.
        self._needs_reset = False
        
    #
    # Layer maintainance ...
    #

    def _flag_needs_reset(self):
        """Set .needs_reset to True if the state of the layers implies 
        that an reset is needed.  If the premise isn't true, the flag 
        remains unchanged."""

        # A changed, drawed layer implies an reset ...

        for layer in self._layers:
            if layer.has_changes() and layer in self._drawn_layers:
                self._needs_reset = True

    def add_layer(self, layer):
        """Add a layer to the Renderer.  It will only be added if it 
        has not been added yet."""

        if layer not in self._layers:
            self._layers.append(layer)

    def remove_layer(self, layer):
        """Remove a layer from the Renderer.  Removing an nonexistent 
        layer will be silently ignored."""

        if layer in self._layers:
            self._layers.remove(layer)

            # Flag that a reset is needed:
            self._needs_reset = True
    
    #
    # Rendering ...
    #

    def _render(self):
        """Render the layers to the FigureAxes.  The FigureAxes may be 
        clear()'ed during this."""

        # Reset eventually ...

        self._flag_needs_reset()

        if self._needs_reset:
            # Clear the axes, the list of drawn layers, and the flag.
            self.figure_axes.clear()
            self._layers_drawn = []
            self._needs_reset = False

        # Draw all layers which are not drawn yet ...

        for layer in self.layers:
            if layer in self._layers_drawn:
                # The layer does not need to be drawn.
                continue

            layer.to_axes(self.axes)

            layer.unset_changed()
            self._layers_drawn.append(layer)
