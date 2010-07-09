# Copyright (c) 2010 Friedrich Romstedt <friedrichromstedt@gmail.com>
# See also <www.friedrichromstedt.org> (if e-mail has changed)
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

# Developed since: May 2010

"""Defines a canvas class for stacks.  It handles events like starting and
stopping zooming and panning, as well as motion related to this.  All
coordinates handed over are figure-relative.

To actually control some Figure, a matplotlayers.backends.*.FigureCanvas must
be created, and the StackCanvas instance has to be added to the FigureCanvas
as a client via figure_canvas.register(stack_canvas).  This will instruct the
FigureCanvas to forward the events to the stack_canvas.  The task of the 
FigureCanvas is, to translate the events from the backend system to the 
figure frame of reference."""


class StackCanvas:
    def __init__(self, stack, 
                zoom_response_both = None, 
                zoom_response_x = None, zoom_response_y = None,
                pan_response_both = None,
                pan_response_x = None, pan_response_y = None):
        """STACK is a matplotlayers.Stack instance.
        
        During zoom, when moving the cursor one edge length of the Stack 
        (either x or y), the zoom response is ZOOM_REPONSE_X/Y.  
        ZOOM_REPONSE_BOTH overrides both ZOOM_RESPONSE_X and ZOOM_REPONSE_Y.  
        The zoom responses for x and y default to 64.
        
        During pan, PAN_RESPONSE_* set the relation of the distance moved and
        the distance the data is moved by the pan.  A response of 1.0 (the
        default) moves the data as much as the curser has been moved.  A 
        response of 0.5 moves the data only half that far.  Setting a 
        response to 0.0 disables panning in that dimension."""
    
        # We set defaults for ZOOM_RESPONSE_X/Y only in __init__().  In 
        # set_zoom_response a non-set value corresponds to "keep the current
        # state".
        # Because ZOOM_RESPONSE_BOTH overrides RESPONSE_X and _Y, we do not 
        # set a default value for ZOOM_RESPONSE_BOTH.

        if zoom_response_x is None:
            zoom_response_x = 64

        if zoom_response_y is None:
            zoom_response_y = 64

        self.set_zoom_response(
                zoom_response_both = zoom_response_both,
                zoom_response_x = zoom_response_x,
                zoom_response_y = zoom_response_y)

        # Same as for the ZOOM_RESPONSE_* variables applies to the 
        # PAN_RESPONSE_* variables.

        if pan_response_x is None:
            pan_response_x = 1.0

        if pan_response_y is None:
            pan_response_y = 1.0

        self.set_pan_response(
                pan_response_both = pan_response_both,
                pan_response_x = pan_response_x,
                pan_response_y = pan_response_y)

        self.stack = stack
        self.motion_mode = None

    #
    # Attribute adjustment methods ...
    #

    def set_zoom_response(self,
            zoom_response_both = None,
            zoom_response_x = None,
            zoom_response_y = None):
        """ZOOM_RESPONSE_BOTH overrides both ZOOM_RESPONSE_X and 
        ZOOM_RESPONSE_Y.  No defaults are set.  If the zoom response is not
        specified for either x or y, the current setting is maintained.
        
        Setting a response to zero disables zooming in that dimension.  This
        means, that also autozooming settings are not affected by manual
        zooming in the respective dimension."""

        # Let ZOOM_RESPONSE_BOTH override ...

        if zoom_response_both is not None:
            zoom_response_x = zoom_response_both
            zoom_response_y = zoom_response_both
        
        # Set the values specified ...

        if zoom_response_x is not None:
            self.zoom_response_x = zoom_response_x

        if zoom_response_y is not None:
            self.zoom_response_y = zoom_response_y

    def set_pan_response(self,
            pan_response_both = None,
            pan_response_x = None,
            pan_response_y = None):
        """PAN_RESPONSE_BOTH overrides both PAN_RESPONSE_X and
        PAN_RESPONSE_Y.  No defaults are det.  If the pan response is not 
        specified for either x or y, the current setting is maintained.
        
        Setting a response to zero disables panning in that dimension.  This
        means, that also autozooming settings are not affected by panning in
        the respective dimension."""

        # Let PAN_RESPONSE_BOTH override ...

        if pan_response_both is not None:
            pan_response_x = pan_response_both
            pan_response_y = pan_response_both

        # Set the values specified ...

        if pan_response_x is not None:
            self.pan_response_x = pan_response_x

        if pan_response_y is not None:
            self.pan_response_y = pan_response_y

    #
    # Coordinate system transformation methods ...
    #

    def figurecoords2axescoords(self, (figurex, figurey)):
        """Map figure relative coordinates (FIGUREX, FIGUREY) to axes
        relative coordinates."""

        bbox = self.stack.axes.get_position()
        
        return ((figurex - bbox.x0) / bbox.size[0],
                (figurey - bbox.y0) / bbox.size[1])

    def axescoords2datacoords(self, (axesx, axesy)):
        """Map axes relative coordaintes (AXESX, AXESY) to data relative
        coordinates."""

        (xstart, xstop) = self.stack.get_xlim()
        (ystart, ystop) = self.stack.get_ylim()

        return (xstart * (1 - axesx) + xstop * axesx,
                ystart * (1 - axesy) + ystop * axesy)

    #
    # Client methods with respect to the StackCanvas ...
    #

    # Determination if a event location applies to us ...

    def event_location_applies(self, figurecoords):
        """Determine whether the figure coordinates FIGURECOORDS are inside
        of the association Stack."""

        (axesx, axesy) = self.figurecoords2axescoords(figurecoords)

        return (0 <= axesx <= 1) and (0 <= axesy <= 1)

    # Zoom methods ...
    
    def autozoom(self):
        """Turn on autoscaling on x and y."""

        self.stack.set_autoscale_on(True)

    def start_zoom(self, figurecoords):
        """Initialise zooming around figure coordinates FIGURECOORDS."""

        # Retrieve needed values.
        (xstart, xstop) = self.stack.get_xlim()
        (ystart, ystop) = self.stack.get_ylim()

        # Store the position where the zoom is fixed.  This means, this 
        # position does not change during zooming.
        axescoords = self.figurecoords2axescoords(figurecoords)
        self.zoom_begin_position_axes = axescoords

        # Store the data to calculate the new view limits later.
        self.zoom_begin_position_data = self.axescoords2datacoords(axescoords)
        (beginx, beginy) = self.zoom_begin_position_data
        self.zoom_begin_distances = \
                ((xstart - beginx, xstop - beginx),
                 (ystart - beginy, ystop - beginy))

        # Set the motion mode.
        self.motion_mode = 'zoom'

    def zoom(self, figurecoords):
        """Zoom with a motion to figure coordinates FIGURECOORDS."""

        # Retrieve needed data ...

        (axesx, axesy) = self.figurecoords2axescoords(figurecoords)
        (begin_axesx, begin_axesy) = self.zoom_begin_position_axes
        (begin_datax, begin_datay) = self.zoom_begin_position_data

        # Calculate the zoom response ...

        (motion_axesx, motion_axesy) = \
                (axesx - begin_axesx, axesy - begin_axesy)

        (factor_x, factor_y) = \
                (self.zoom_response_x ** (-motion_axesx),
                 self.zoom_response_y ** (-motion_axesy))

        # Calculate the new view limits ...

        ((tostart_x, tostop_x), (tostart_y, tostop_y)) = \
                self.zoom_begin_distances

        ((tostart_x, tostop_x), (tostart_y, tostop_y)) = \
                ((tostart_x * factor_x, tostop_x * factor_x),
                 (tostart_y * factor_y, tostop_y * factor_y))

        (newlim_x, newlim_y) = \
                ((begin_datax + tostart_x, begin_datax + tostop_x),
                 (begin_datay + tostart_y, begin_datay + tostop_y))

        # Apply the new view limits ...
        #
        # Do apply the new view limits only if zooming is not disabled in 
        # the respective dimension.

        if self.zoom_response_x != 0:
            self.stack.set_xlim(newlim_x)

        if self.zoom_response_y != 0:
            self.stack.set_ylim(newlim_y)

    def stop_zoom(self):
        """Set the motion mode to None."""
        
        self.motion_mode = None

    # Pan mathods ...

    def start_pan(self, figurecoords):
        """Prepare panning of figure position FIGURECOORDS."""

        # Calculate the ratio of data scale to axes scale.  This is the
        # data range covered by the axes extent in x and y, respectively.

        # Retrieve the view limits:
        ((startx, stopx), (starty, stopy)) = \
                (self.stack.get_xlim(), self.stack.get_ylim())

        # Store the initial view limits:
        self.pan_begin_limits = \
                ((startx, stopx), (starty, stopy))

        # Calculate the pan ratio:
        bbox = self.stack.axes.get_position()
        self.pan_ratio = (stopx - startx, stopy - starty)

        # Store the initial pan position in axes coordinates.

        self.pan_begin_position_axes = \
                self.figurecoords2axescoords(figurecoords)

        # Set the motion mode.

        self.motion_mode = 'pan'

    def pan(self, figurecoords):
        """Perform a pan of the initial pan position to the current cursor
        position at figure coordinates FIGURECOORDS."""

        # Calculate the move in data coordinates ...

        # Retrieve the coordinates in the axes frame.
        (axesx, axesy) = self.figurecoords2axescoords(figurecoords)

        # Calculate the move in the axes frame.
        (begin_axesx, begin_axesy) = self.pan_begin_position_axes
        (move_axesx, move_axesy) = (axesx - begin_axesx, axesy - begin_axesy)

        # Calculate the move in the data frame.
        (pan_ratiox, pan_ratioy) = self.pan_ratio
        (move_datax, move_datay) = \
                (self.pan_response_x * move_axesx * pan_ratiox, 
                 self.pan_response_y * move_axesy * pan_ratioy)

        # Compensate for the move.  Calculate the new limits.
        ((startx, stopx), (starty, stopy)) = self.pan_begin_limits
        ((startx, stopx), (starty, stopy)) = \
                ((startx - move_datax, stopx - move_datax),
                 (starty - move_datay, stopy - move_datay))

        # Set the new limits.
        self.stack.set_xlim((startx, stopx))
        self.stack.set_ylim((starty, stopy))

    def stop_pan(self):
        """Clears the motion mode."""

        self.motion_mode = None

    # Motion methods ...

    def motion(self, figurecoords):
        """Interpret a motion of the cursor to figure coordinates
        FIGURECOORDS according to the current motion mode."""

        if self.motion_mode == 'zoom':
            # We zoom currently.
            self.zoom(figurecoords)

        elif self.motion_mode == 'pan':
            # We pan currently.
            self.pan(figurecoords)
