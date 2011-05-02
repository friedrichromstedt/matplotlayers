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

"""Defines the Stack class, an abstraction of Axes, providing the framework 
to hold a stack of layers."""

import matplotlib.figure
import matplotlib.ticker


class Stack:
    """Abstraction of Axes, providing the framework to hold a stack of layers.
    
    A Stack is associated necessarily with exactly one matplotlib.axes.Axes 
    instance.  The Axes instance can be handed over, or can be created during 
    initialisation from a Figure provided by the user.
    
    There is no association with a Figure, except that during initialisation
    time, the Axes may be created by using the Figure handed over by the
    user."""
    
    #
    # Initialisation methods ...
    #

    def __init__(self, 
            figure,
            left = 0.2, bottom = 0.2, width = 0.6, height = 0.6,
            axes = None,
            polar = None,
            autoscale_both_on = None,
            autoscale_x_on = None,
            autoscale_y_on = None,
            colorbar=None,
            locator_x=None,
            locator_y=None):
        """FIGURE is the matplotlib.figure.Figure instance where to act on.
        AXES is optionally an existing axes instance.  If AXES is not given,
        a new axes instance will be created, either a cartesian, or a polar if
        POLAR is True.
        
        The initial autoscaling is controled by AUTOSCALING_BOTH, 
        AUTOSCALING_X, and AUTOSCALING_Y.  If AUTOSCALING_BOTH is given, it
        overrides AUTOSCALING_X and AUTOSCALING_Y.  If the autoscaling for 
        some axis isn't given (either by AUTOSCALING_BOTH or by the other
        arguments), it defaults to True.
        
        If COLORBAR isn't None, but 'vertical' or 'horizontal', the Axes
        will be initialised by setting the label and ticks position to the
        appropriate position.  This is useful if the Stack is intended to be
        used for a LayerColorbar, since the LayerColorbar cannot draw a
        Colorbar until it has received data, and therefore there would be
        nothing updating the ticks and label positions.
        
        LOCATOR_X and LOCATOR_Y are optional and are the major locator to be
        used for the respective axes."""

        # Define the default values for AUTOSCALING_X/Y.  May be overridden
        # by AUTOSCALING_BOTH if that is given ...

        if autoscale_x_on is None:
            autoscale_x_on = True
        if autoscale_y_on is None:
            autoscale_y_on = True
    
        # Initialise attributes ...

        if axes is None:
            # Create a new axes instance.
            axes = figure.add_axes(
                    (left, bottom, width, height),
                    polar = polar)
            axes.hold(True)

        # Take over the axes.
        self.axes = axes

        # Initialise the title etc. to some values.
        self.title = self.axes.get_title()
        self.title_kwargs = {}
        self.xlabel = self.axes.get_xlabel()
        self.ylabel = self.axes.get_ylabel()

        # Apply the autoscaling ...
        #
        # This will also store the correct values for .xlim and .ylim.
        
        self.set_autoscale_on(
                both_on = autoscale_both_on,
                x_on = autoscale_x_on,
                y_on = autoscale_y_on)

        # Store the locators ...

        self.set_locators(locator_x=locator_x, locator_y=locator_y)

        # Prepare for use as a colorbar ...
        #
        # Do this after setting the locators and not before.  Because
        # set_colorbar() sets also the xticks, but set_locators overrides
        # this by setting the xlocator to AutoLocator(), when done in the
        # wrong order.

        self.set_colorbar(colorbar)
    
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
            if layer.has_changed() and \
                    id(layer) in map(id, self._layers_drawn):
                self._needs_reset = True

    def add_layer(self, layer):
        """Add a layer to the Renderer.  It will only be added if it 
        has not been added yet."""

        if id(layer) not in map(id, self._layers):
            self._layers.append(layer)

    def remove_layer(self, layer):
        """Remove a layer from the Renderer.  Removing an nonexistent 
        layer will be silently ignored."""

        if id(layer) in map(id, self._layers):
            self._layers.remove(layer)

            # Flag that a reset is needed:
            self._needs_reset = True
    
    #
    # Rendering ...
    #

    def render(self):
        """Render the layers to the Stack.  The Stack may be clear()'ed during 
        this."""

        # Reset eventually ...

        self._flag_needs_reset()

        if self._needs_reset:
            # Clear the axes, the list of drawn layers, and the flag.
            self.clear()
            self._layers_drawn = []
            self._needs_reset = False

        # Draw all layers which are not drawn yet ...

        for layer in self._layers:
            if id(layer) in map(id, self._layers_drawn):
                # The layer does not need to be drawn.
                continue

            layer.to_axes(self.axes)

            layer.unset_changed()
            self._layers_drawn.append(layer)

    #
    # Property set methods ...
    #
        
    def set_title(self, title, **title_kwargs):
        """Set the title to string TITLE with kwargs *title_kwargs*."""

        self.axes.set_title(title, **title_kwargs)
        self.title = title
        self.title_kwargs = title_kwargs

    def set_xlabel(self, xlabel):
        """Set the xlabel to string XLABEL."""

        self.axes.set_xlabel(xlabel)
        self.xlabel = xlabel

    def set_ylabel(self, ylabel):
        """Set the ylabel to string YLABEL."""

        self.axes.set_ylabel(ylabel)
        self.ylabel = ylabel

    def set_xlim(self, lim):
        """Sets the limit and the stored value for restoration in .clear().
        If LIM isn't None, autoscaling in x will be turned off, else it will
        be turned on."""

        if lim is not None:
            # This turns autoscaling off, maintaining the current xlim.
            self.set_autoscale_on(x_on = False)

            # This sets and stores the *new* xlim.
            self.axes.set_xlim(lim)
            self.xlim = lim

        else:
            # Turn autoscaling on, which will also store None in .xlim.
            self.set_autoscale_on(x_on = True)

    def set_ylim(self, lim):
        """Sets the limit and the stored value for restoration in .clear().
        If LIM isn't None, autoscaling in y will be turned off, else it will
        be turned on."""

        if lim is not None:
            # This turns autoscaling off, maintaining the current ylim.
            self.set_autoscale_on(y_on = False)

            # This sets and stores the *new* ylim.
            self.axes.set_ylim(lim)
            self.ylim = lim

        else:
            # Turn autoscaling on, which will also store None in .ylim.
            self.set_autoscale_on(y_on = True)
        
    def set_autoscale_on(self, both_on = None, x_on = None, y_on = None):
        """The autoscaling is controled by BOTH_ON, X_ON, and Y_ON.  If 
        BOTH_ON is given, it overrides X_ON and Y_ON.  If the autoscaling for 
        some axis isn't given (either by BOTH_ON or by X_ON or Y_ON), its 
        setting will be maintained."""

        if both_on is not None:
            # Override AUTOSCALING_X/Y.
            x_on = both_on
            y_on = both_on

        if x_on is not None:
            # Set the X autoscaling...
            #
            # Do not call .set_xlim() during that, because this may result in
            # infinite recursion, if .set_autoscale_on() was called by 
            # a .set_Xlim() method.

            self.axes.set_autoscalex_on(x_on)
            if x_on:
                # This signals .clear() that no limit shall be preserved.
                self.xlim = None
            else:
                # Signal .clear() the correct xlim.  If .autoscale_x_on was 
                # True, then .xlim is currently None.
                self.xlim = self.axes.get_xlim()
            self.autoscale_x_on = x_on

        if y_on is not None:
            # Set the Y autoscaling ...
            
            self.axes.set_autoscaley_on(y_on)
            if y_on:
                # This signals .clear() that no limit shall be preserved.
                self.ylim = None
            else:
                # Signal .clear() the correct ylim.  If .autoscale_y_on was 
                # True, then .ylim is currently None.
                self.ylim = self.axes.get_ylim()
            self.autoscale_y_on = y_on
        
        # Apply the autoscaling if needed ...

        # If X_ON or Y_ON is None, this evaluates as False, i.e., no problem
        # with None values supplied for X/Y_ON.
        if x_on or y_on:
            self.axes.autoscale_view()

    def _update_colorbar_mode(self):
        """Ensures the colorbar mode if present.  Note that returning from
        colorbar mode to normal mode will not work properly except you
        do a .clear()."""

        # Copied from matplotlib.colorbar.ColorbarBase.config_axis().

        if self.colorbar == 'vertical':
            self.axes.xaxis.set_ticks([])
            self.axes.yaxis.set_label_position('right')
            self.axes.yaxis.set_ticks_position('right')

        elif self.colorbar == 'horizontal':
            self.axes.yaxis.set_ticks([])
            self.axes.xaxis.set_label_position('bottom')

    def set_colorbar(self, colorbar):
        """Sets the colorbar mode."""

        self.colorbar = colorbar
        self._update_colorbar_mode()

    def set_locators(self, locator_x, locator_y):
        """Sets the locators to be used.  None means 'default locator'."""

        self.locator_x = locator_x
        self.locator_y = locator_y

        # Set locators ...

        if self.locator_x is not None:
            self.axes.xaxis.set_major_locator(self.locator_x)
        else:
            self.axes.xaxis.set_major_locator(matplotlib.ticker.AutoLocator())

        if self.locator_y is not None:
            self.axes.yaxis.set_major_locator(self.locator_y)
        else:
            self.axes.yaxis.set_major_locator(matplotlib.ticker.AutoLocator())

    #
    # Clearing method ...
    #

    def clear(self):
        """Clears the axes, maintaining autoscaling setting, xlim, ylim, 
        title, xlabel, and ylabel.  If autoscaling is on for an axis, the
        limit will not be maintained, it will default then to (0.0, 1.0)."""

        # Put the axes back into initial state ...

        self.axes.clear()

        # Restore the settings stored ...

        # Restore labeling.
        self.set_title(self.title, **self.title_kwargs)
        self.set_xlabel(self.xlabel)
        self.set_ylabel(self.ylabel)
        
        # Restore colorbar mode
        self._update_colorbar_mode()

        # Restore locators
        if self.locator_x is not None:
            self.axes.xaxis.set_major_locator(self.locator_x)
        if self.locator_y is not None:
            self.axes.yaxis.set_major_locator(self.locator_y)

        # Restore lims.  If autoscaling was turned on, the corresponding
        # limit will be None, and the setting is maintained, because
        # autoscaling on is the default state.  If autoscaling was turned off,
        # the corresponding limit will be set, and the autoscaling will be
        # turned off in the .axes by the .set_Xlim() call.
        if self.xlim is not None:
            self.set_xlim(self.xlim)

        if self.ylim is not None:
            self.set_ylim(self.ylim)

    #
    # Property get methods ...
    #

    def get_title(self):
        """Returns the title set for the axes."""

        return self.title

    def get_xlabel(self):
        """Returns the xlabel set for the axes."""

        return self.xlabel
    
    def get_ylabel(self):
        """Returns the ylabel set for the axes."""

        return self.ylabel

    def get_xlim(self):
        """Return the *actual* xlimit.  This may change during autoscaling."""

        return self.axes.get_xlim()

    def get_ylim(self):
        """Return the *actual* ylimit.  This may change during autoscaling."""

        return self.axes.get_ylim()
        
    def get_autoscale_on(self):
        """Return if both x and y autoscaling is active for the axes (logical 
        AND)."""

        return self.axes.get_autoscale_on()

    def get_autoscalex_on(self):
        """Return if x autoscaling is active for the axes."""

        return self.axes.get_autoscalex_on()

    def get_autoscaley_on(self):
        """Return if y autoscaling is active for the axes."""

        return self.axes.get_autoscaley_on()
