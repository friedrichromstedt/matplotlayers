# Copyright (c) 2008, 2009, 2010 Friedrich Romstedt
# <friedrichromstedt@gmail.com> <www.friedrichromstedt.org>
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

# Developed since: Aug 2008

"""The panel class PanelFigureAxes is responsible for updating, zooming, and
panning of a FigureAxes instance."""


class PanelFigureAxes:
    r"""This class is responsible for updating, zooming, and panning of a
    FigureAxes instance.  It receives its input events from a matplotlayers.\
    backends.tk.panels.figure_canvas.FigureCanvas instance."""

	def __init__(self, master, figure_axes,
			callback_start_zoom, callback_zoom,
			callback_start_pan, callback_pan,
			callback_autozoom,
			callback_show_settings,
			image_generator,
			shape = None,
            figure_canvas = None):
        r"""FIGURE_AXES is the matplotlayers.FigureAxes instance.  CALLBACK_* 
        are the event handlers to call back.  IMAGE_GENERATOR is a function
        generating an image from shape parameter.  SHAPE is the initial shape
        of the drawing matplotlayers.backends.tk.panels.figure_canvas.\
        FigureCanvas if not FIGURE_CANVAS is given.  If SHAPE is used and a 
        new FigureCanvas is created, then the Canvas will be pack()ed with
        expand=True and fill=Tkinter.BOTH.  The default SHAPE is (300, 300)."""

		if shape is None:
			shape = (300, 300)

        self.figure_axes = figure_axes

		self.callback_start_zoom = callback_start_zoom
		self.callback_zoom = callback_zoom
		self.callback_start_pan = callback_start_pan
		self.callback_pan = callback_pan
		self.callback_autozoom = callback_autozoom
		self.callback_show_settings = callback_show_settings
		self.image_generator = image_generator

		self.motion_origin = None
		self.zoom_origin = None
		self.zoom_initial_distances = None
		self.pan_cursor = None
		self.motion_mode = 'none'

    def check_inside(self, figurecoords):
        """Return True if FIGURECOORDS are inside the .figure_axes instance,
        else returns False."""

        return 

	def tk_start_zoom(self, figurecoords):
        
		self.motion_origin = figurecoords
		self.motion_mode = 'zoom'
		self.zoom_origin = figurecoords
		self.event_handler_start_zoom(figurecoords)

	def tk_start_pan(self, figurecoords):
		self.pan_origin = figurecoords
		self.motion_mode = 'pan'
		self.event_handler_start_pan()

	def tk_stop_zoom(self):
		self.motion_mode = 'none'

	def tk_stop_pan(self):
		self.motion_mode = 'none'

	def tk_autozoom(self):
		self.event_handler_autozoom()

	def tk_show_settings(self, event):
		self.event_handler_settings()

	def tk_motion(self, event):
		if self.motion_mode == 'zoom':
			pixel_distances = (self.motion_origin[0] - event.x,
					event.y - self.motion_origin[1])
			factors=[(2.0 ** (pixel_distances[i] * 0.02)) for i in (0,1)]
			self.event_handler_zoom(factors)
			self.update()
		elif self.motion_mode == 'pan':
			disp_coords = self.map_to_display((event.x, event.y))
			compensate = [disp_coords[i] - self.pan_origin[i] for i in (0,1)]
			self.event_handler_pan(compensate)
			self.update()


