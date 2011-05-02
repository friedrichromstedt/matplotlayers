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

# Last changed: 2010 Mar 13
# Developed since: Jul 2008
# File version: 0.1.0b

import matplotlayers.layer
import keyconf


class LayerPColorMesh(matplotlayers.layer.Layer):
    def __init__(self, **kwargs):
        """CMAP may be an abbreviation as defined by matplotlib, it defaults 
        to 'gray'.  The kwarg LAYER_COLORBAR may be a matplotlayers.\\
        LayerColorbar instance.
        
        The layer is specified empty, if X, Y, or C are not specified or
        None."""

        kwargs.setdefault('cmap', 'gray')

        matplotlayers.layer.Layer.__init__(self)

        # Unfortunately, mpl pcolor needs X, Y, C positional.
        # So we have to hide X, Y and C config away.
        self._XYC = keyconf.Configuration()
        self.add_components(XYC = self._XYC)
        self.set_aliases(X = 'XYC_X', Y = 'XYC_Y', C = 'XYC_C')

        # We forward non-pcolormesh arguments to some dedicated Configuration, 
        # because they should not show up in the call to pcolormesh().
        self._explicits = keyconf.Configuration()
        self.add_components(explicits=self._explicits)
        self.set_aliases(layer_colorbar='explicits_layer_colorbar')
        
        self.configure(**kwargs)

    def to_axes(self, axes):
        """Plot the data to matplotlib.axes.Axes instance AXES."""
        
        # Skip plotting if not all data is specified ...

        if not self.is_configured('X') or \
                not self.is_configured('Y') or \
                not self.is_configured('C'):
            return

        # Plot ...

        # Unfortunately, mpl pcolor needs X, Y, C positional.
        X = self['X']
        Y = self['Y']
        C = self['C']
        # X, Y, C are actually stored in ._XYC.

        mappable = axes.pcolormesh(X, Y, C, **self)

        # Notify also the LayerColorbar of the new mappable.
        if self.is_configured('layer_colorbar'):
            self['layer_colorbar'].set_mappable(mappable)
