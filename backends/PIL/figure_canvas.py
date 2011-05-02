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

# Developed since: Jul 2008

"""Defines a Canvas for a matplotlib.figure.Figure instance to be rendered as 
a PIL image."""

import PIL.Image
import matplotlib.backends.backend_agg as mpl_backend_agg


class FigureCanvasPIL:
    """A canvas for a matplotlib.figure.Figure instance to be rendered as a
    PIL image."""

    def __init__(self, figure):
        """FIGURE is a matplotlib.figure.Figure instance."""

        self.figure = figure

    def output_PIL(self, shape):
        """SHAPE is in pixels."""

        dpi = self.figure.dpi
        self.figure.set_size_inches(
                float(shape[0]) / dpi,
                float(shape[1]) / dpi)

        agg_canvas = mpl_backend_agg.FigureCanvasAgg(self.figure)
        agg_canvas.draw()
        image_string = agg_canvas.tostring_rgb()

        image = PIL.Image.fromstring("RGB", shape, image_string)
        return image
