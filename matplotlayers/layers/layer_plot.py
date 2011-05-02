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

__version__ = (0, 1, 0)

import matplotlayers.layer
import keyconf
import numpy

"""Plotting layer with functionality similar to the axes.plot() method."""


class LayerPlot(matplotlayers.layer.Layer):
    """Plotting layer calling the axes.plot() method."""

    def __init__(self,
            x = None, y = None,
            xerr = None, yerr = None,
            x_ua = None, y_ua = None,
            envelope_on = None,
            sigmas = None,
            **kwargs):
        """X and Y are the datasets of equal, one-dimensionsional shape.
        All other arguments are optional.  XERR and YERR specify the resp. 
        errors.  X_UA and Y_UA specify X and Y to be some upy.undarray class 
        instance or similar with .value and an .uncertaintly() method.  SIGMAS
        will be handed over to this .uncertainty() method unchanged. 
        ENVELOPE_ON turns the envelope on.  The LayerPlot can be set to empty 
        by not specifiying X or Y.
        
        Further configuration of the plot commands can be done via **kwargs.
        All arguments not starting with 'envelope_' will be handed over to
        the plot() call, all those starting with 'envelope_' will be handed 
        over to the envelope plot() call for the envelope with the 'envelope_'
        stripped."""

        if envelope_on is None:
            envelope_on = False

        matplotlayers.layer.Layer.__init__(self)

        # Register the envelope component ...
        #
        # All keys starting with 'envelope_' will be forwarded.

        self._envelope = keyconf.Configuration()
        self.add_components(envelope = self._envelope)

        # Register the component storing error values, which shall in 
        # envelope mode not be given to the plot command.

        self._err = keyconf.Configuration()
        self.add_components(err = self._err)

        self.configure(envelope_on = envelope_on, **kwargs)

        # Forward also xerr and yerr to ._err:
        self.set_aliases(xerr = 'err_x', yerr = 'err_y')

        self.set_x(x, xerr, x_ua, sigmas)
        self.set_y(y, yerr, y_ua, sigmas)


    #
    # Plotting methods ...
    #

    def to_axes(self, axes):
        """Perform plotting to matplotlib.axes.Axes instance AXES.  The
        layer will not perform any plotting if .x or .y isn't set."""
    
        # Skip plotting if x or y are not set ...

        if not self.is_configured('x') or not self.is_configured('y'):
            return 
    
        # Plot ...

        if self.get_config('envelope_on'):

            if self.is_configured('xerr') and self.is_configured('yerr'):
                raise ValueError(
                        "Cannot draw envelope for xerr and yerr both.")

            # Perform default center plot.
            #
            # Layer is derived from Configuration, which is a dict containing
            # the keys.  err_x and err_y are in the err component and not
            # visible here.
            axes.errorbar(**self)

            # Perform envelope plot.
            if self.is_configured('xerr'):
                x = self.get_config('x')
                xerr = self.get_config('xerr')
                
                if xerr.ndim == 1:
                    left = x - xerr
                    right = x + xerr
                elif xerr.ndim == 2:
                    left = x - xerr[0]
                    right = x + xerr[1]
        
                left_kwargs = dict(self._envelope)
                del left_kwargs['on']
                left_kwargs['x'] = left
                left_kwargs['y'] = self.get_config('y')

                axes.errorbar(**left_kwargs)

                right_kwargs = dict(self._envelope)
                del right_kwargs['on']
                right_kwargs['x'] = right
                right_kwargs['y'] = self.get_config('y')

                axes.errorbar(**right_kwargs)

            elif self.is_configured('yerr'):
                y = self.get_config('y')
                yerr = self.get_config('yerr')
                
                if yerr.ndim == 1:
                    bottom = y - yerr
                    top = y + yerr
                elif yerr.ndim == 2:
                    bottom = y - yerr[0]
                    top = y + yerr[1]

                bottom_kwargs = dict(self._envelope)
                del bottom_kwargs['on']
                bottom_kwargs['x'] = self.get_config('x')
                bottom_kwargs['y'] = bottom

                axes.errorbar(**bottom_kwargs)

                top_kwargs = dict(self._envelope)
                del top_kwargs['on']
                top_kwargs['x'] = self.get_config('x')
                top_kwargs['y'] = top

                axes.errorbar(**top_kwargs)

        else:
            # Perform normal plotting.

            # Copy the err_* arguments:
            xerr = None
            yerr = None

            if self.is_configured('xerr'):
                xerr = self.get_config('xerr')

            if self.is_configured('yerr'):
                yerr = self.get_config('yerr')

            axes.errorbar(
                    xerr = xerr,
                    yerr = yerr,
                    **self)

    #
    # x data methods ...
    #

    def set_x(self, x = None, xerr = None, x_ua = False, sigmas = None):
        """Sets the x data and the xerror data.  Without X_UA, X is the value,
        and XERR is the error.  With X_UA, XERR is ignored, the value is 
        X.value, and the error is X.uncertainty(SIGMAS), where SIGMAS is 
        handed over unchanged.

        Values not specified are left untouched."""
            
        # Interpret arguments ...
        
        if x_ua:
            value = x.value
            # SIGMAS = None uses upy's default:
            xerr = x.uncertainty(sigmas)
        else:
            if x is not None:
                value = numpy.asarray(x)
            else:
                value = None

            if xerr is not None:
                xerr = numpy.asarray(xerr)
        
        # Apply values ...
        
        self.configure(x = value, xerr = xerr)
    
    #
    # y data methods ...
    #

    def set_y(self, y, yerr = None, y_ua = False, sigmas = None):
        """Sets the y data and yerror data.  Without Y_UA, Y is the value,
        and YERR is the error.  With Y_UA, YERR is ignored, the value is 
        Y.value, and the error is Y.uncertainty(SIGMAS), where SIGMAS is 
        handed over unchanged.
        
        Values not specified are left untouched."""
    
        # Interpret arguments ...

        if y_ua:
            value = y.value
            # SIGMAS = None uses up's default:
            yerr = y.uncertainty(sigmas)
        else:
            if y is not None:
                value = numpy.asarray(y)
            else:
                value = None

            if yerr is not None:
                yerr = numpy.asarray(yerr)
        
        # Apply values ...

        self.configure(y = value, yerr = yerr)
