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

"""The FigureCanvasTk class draws a matplotlayers.backend.PIL.FigureCanvas to 
Tkinter via a Tkinter.Canvas instance.

To actually control some Stack, a matplotlayers.backends.StackCanvas must be 
created, and this StackCanvas has to be added to the FigureCanvas as a client 
via figure_canvas.register(stack_canvas).  This will forward all the mouse 
events to the stack_canvas, making it controllable.  The benefit of this 
approach is, that several StackCanvases can be controlled by the same 
FigureCanvas, thus making panning and zooming several Axes in a Figure easy."""

import Tkinter
import PIL.ImageTk
import matplotlayers.backends.tk  # for .has_mainloop
import matplotlayers.backends.tk.stack_settings
import matplotlayers.backends.tk.figure_settings


class FigureCanvasTk:
    def __init__(self, master, 
            figure,
            shape = None,
            tk_canvas = None):
        """figure is a matplotlib.figure.Figure instance.  SHAPE is the extent 
        of the Tkinter.Canvas if a new one is created.  TK_CANVAS can be used 
        to hand over an already-existing Tkinter.Canvas to draw upon.  If a 
        new Tkinter.Canvas is created, it is .pack()ed with arguments 
        expand=True and fill=Tkinter.BOTH.  The default SHAPE is (400, 400).  
        MASTER is only used when a new Tkinter.Canvas is created."""

        if shape is None:
            shape = (400, 400)

        # Initialise attributes ...

        self.figure = figure
        self.PIL_canvas = matplotlayers.backends.PIL.FigureCanvasPIL(figure)

        self.pixelsize = None
        (self.photoimage, self.photoimage_tag) = (None, None)

        # Create Tkinter.Canvas if necessary ...

        if tk_canvas is None:
            self.tk_canvas = Tkinter.Canvas(master,
                    highlightthickness=0,
                    background='white',
                    width=shape[0],
                    height=shape[1])

        # Initialise client registry ...

        self.clients = []

        # Bind methods ...

        # Windows:  Use Buttons 1 & 3  (at least with my 3-button mouse)
        # Mac:  Use Buttons 1 & 2  (at least with my MacBook)
        # => So we bind to both buttons 2 & 3 for the right-click.

        self.tk_canvas.bind('<Configure>', self.tk_configure, add=True)
        self.tk_canvas.bind('<ButtonPress-1>', self.tk_start_zoom, add=True)
        self.tk_canvas.bind('<ButtonPress-2>', self.tk_start_pan, add=True)
        self.tk_canvas.bind('<ButtonPress-3>', self.tk_start_pan, add=True)
        self.tk_canvas.bind('<ButtonRelease-1>', self.tk_stop_zoom, add=True)
        self.tk_canvas.bind('<ButtonRelease-2>', self.tk_stop_pan, add=True)
        self.tk_canvas.bind('<ButtonRelease-3>', self.tk_stop_pan, add=True)
        self.tk_canvas.bind('<Motion>', self.tk_motion, add=True)
        self.tk_canvas.bind('<Double-Button-1>', self.tk_show_figure_settings,
                add=True)
        self.tk_canvas.bind('<Double-Button-2>', self.tk_show_stack_settings, 
                add=True)
        self.tk_canvas.bind('<Double-Button-3>', self.tk_show_stack_settings, 
                add=True)

        # Pack Tkinter.Canvas if newly created ...

        if tk_canvas is None:
            self.tk_canvas.pack(expand=True, fill=Tkinter.BOTH)

    #
    # Conversion method ...
    #

    def pixelcoords2figurecoords(self, (pixelx, pixely)):
        """Convert the canvas-relative pixel coordinate (PIXELX, PIXELY) to
        figure-relative float coordinate (figurex, figurey).  PIXELY is zero
        at the top, figurey is zero at the bottom of the figure."""

        return (float(pixelx) / self.pixelsize[0],
                1 - float(pixely) / self.pixelsize[1])

    #
    # Client registry ...
    #

    def register(self, client):
        """Register the client CLIENT to the canvas."""

        if client not in self.clients:
            self.clients.append(client)

    def unregister(self, client):
        """Unregister the client CLIENT from the canvas."""
        
        if client in self.clients:
            self.clients.remove(client)

    #
    # Tk callbacks ...
    #

    def tk_configure(self, event):
        """Called upon reconfiguration of the .tk_canvas ."""

        self.pixelsize = (event.width, event.height)
        self.update()

    def tk_autozoom(self, event):
        """Called upon activation of autozooming."""

        figurecoords = self.pixelcoords2figurecoords((event.x, event.y))
        for client in self.clients:
            if client.event_location_applies(figurecoords):
                client.autozoom()

        self.update()

    def tk_start_zoom(self, event):
        """Called upon start of zooming."""

        figurecoords = self.pixelcoords2figurecoords((event.x, event.y))
        for client in self.clients:
            if client.event_location_applies(figurecoords):
                client.start_zoom(figurecoords)

        self.update()

    def tk_start_pan(self, event):
        """Called upon start of panning."""

        figurecoords = self.pixelcoords2figurecoords((event.x, event.y))
        for client in self.clients:
            if client.event_location_applies(figurecoords):
                client.start_pan(figurecoords)

        self.update()

    def tk_stop_zoom(self, event):
        """Called upon stop of zooming."""

        for client in self.clients:
            client.stop_zoom()

        self.update()

    def tk_stop_pan(self, event):
        """Called upon stop of panning."""

        for client in self.clients:
            client.stop_pan()

        self.update()

    def tk_show_stack_settings(self, event):
        """Called when the settings dialog shall be shown."""

        figurecoords = self.pixelcoords2figurecoords((event.x, event.y))
        for client in self.clients:
            if client.event_location_applies(figurecoords):
                # Create dialog:
                matplotlayers.backends.tk.stack_settings.StackSettings(
                        self.tk_canvas, client.stack, self.update)

    def tk_show_figure_settings(self, event):
        """Called when the Figure settings dialog shall be shown."""

        # Create dialog:
        matplotlayers.backends.tk.figure_settings.FigureSettings(
                self.tk_canvas, self.figure)

    def tk_motion(self, event):
        """Called when the cursor is moved."""

        figurecoords = self.pixelcoords2figurecoords((event.x, event.y))
        for client in self.clients:
            # Pass motion events on the all clients.  Once the start event
            # did apply to a client, also motion events at locations where
            # start events would not apply, shall be passed on.
            client.motion(figurecoords)

        self.update()

    #
    # Update method ...
    #

    def update(self):
        """Redraws the figure."""

        if self.pixelsize is None: 
            # If this is called before .tk_configure() was initialised we 
            # ignore the call silently.
            return
        
        # Retrieve the image.
        image = self.PIL_canvas.output_PIL(self.pixelsize)

        # Store the old photoimage attributes before overwriting them.
        (old_photoimage, old_photoimage_tag) = \
                (self.photoimage, self.photoimage_tag)

        # Create the new photoimage.
        self.photoimage = PIL.ImageTk.PhotoImage(image)

        # Put it on the Canvas before deleting the old one.  This avoids
        # flickering.
        self.photoimage_tag = self.tk_canvas.create_image((0, 0), 
                image = self.photoimage, anchor='nw')

        if old_photoimage is not None and old_photoimage_tag is not None:
            # If there was a previous image, remove it from the Canvas.
            self.tk_canvas.delete(old_photoimage_tag)

        if not matplotlayers.backends.tk.has_mainloop:
            # If we /have/ a mainloop, we /must/ avoid calling .update().
            # This showed up when having a mainloop, crashing the program ...
            # It hung up in irregular widely spread time intervals.  When
            # avoiding the .update() call in this case, everything worked like
            # a charm again.
            self.tk_canvas.update()

    #
    # Tk Destroy method ...
    #

    def destroy(self):
        """Destroys the Canvas associated with this FigureCanvas.  The Canvas
        is destroyed irrespective of whether it was created in .__init__() or
        handed over by the user."""
        
        if self.photoimage is not None and self.photoimage_tag is not None:
            # Remove the image from the Canvas if it exists.
            self.tk_canvas.delete(self.photoimage_tag)

        # Destroy the drawing Canvas.
        self.tk_canvas.destroy()
