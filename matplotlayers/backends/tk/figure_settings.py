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

# Developed since: June 2010

"""Settings of a complete figure, also writing down to HDD."""

import Tkinter
import tkFileDialog
import ventry
import matplotlib.backends.backend_ps
import matplotlib.backends.backend_pdf
import matplotlayers.backends.PIL


class FigureSettings(Tkinter.Toplevel):

    def __init__(self, master, figure):
        """FIGURE is the matplotlib.figure.Figure to act upon."""

        Tkinter.Toplevel.__init__(self, master)
        self.wm_title('Figure Settings')
        self.figure = figure

        # Create Save widgets ...

        # Create structure frames.
        self.lframe_save = Tkinter.LabelFrame(self, text = 'Save')
        self.lframe_save.pack(side = Tkinter.LEFT, anchor = Tkinter.N)

        self.lframe_vector = Tkinter.LabelFrame(self.lframe_save, text = 'Vector Formats')
        self.lframe_vector.pack(side = Tkinter.TOP)
        
        self.lframe_raster = Tkinter.LabelFrame(self.lframe_save, text = 'Pixel Formats')
        self.lframe_raster.pack(side = Tkinter.TOP)


        # Create dimension input inches.
        self.frame_dim_inches = Tkinter.Frame(self.lframe_vector)
        self.frame_dim_inches.pack(side = Tkinter.TOP)

        self.inches_xdim = ventry.NamedVEntry(self.frame_dim_inches,
                name = 'Size X (Inches):',
                column = 0, row = 0,
                initial = 9.0, validate = ventry.number)
        self.inches_ydim = ventry.NamedVEntry(self.frame_dim_inches,
                name = 'Size Y (Inches):',
                column = 0, row = 1,
                initial = 9.0, validate = ventry.number)
        self.inches_xdim.initialise()
        self.inches_ydim.initialise()

        # Create save button EPS.
        self.button_eps = Tkinter.Button(self.lframe_vector,
                text = 'Save EPS ...',
                command = self.tk_save_eps)
        self.button_eps.pack(side = Tkinter.TOP, fill = Tkinter.X)

        # Create save button PDF.
        self.button_pdf = Tkinter.Button(self.lframe_vector,
                text = 'Save PDF ...',
                command = self.tk_save_pdf)
        self.button_pdf.pack(side = Tkinter.TOP, fill = Tkinter.X)


        # Create dimension input pixels.
        self.frame_dim_pixels = Tkinter.Frame(self.lframe_raster)
        self.frame_dim_pixels.pack(side = Tkinter.TOP)

        self.pixels_xdim = ventry.NamedVEntry(self.frame_dim_pixels,
                name = 'Size X (Pixels):',
                column = 0, row = 0,
                initial = 800, validate = ventry.int)
        self.pixels_ydim = ventry.NamedVEntry(self.frame_dim_pixels,
                name = 'Size Y (Pixels):',
                column = 0,row = 1,
                initial = 600,validate = ventry.int)
        self.pixels_xdim.initialise()
        self.pixels_ydim.initialise()

        # Create save image button.
        self.button_img = Tkinter.Button(self.lframe_raster,
                text = 'Save Raster Format ...',
                command = self.tk_save_img)
        self.button_img.pack(side = Tkinter.TOP, fill = Tkinter.X)

    def tk_save_eps(self):
        filename = tkFileDialog.asksaveasfilename(
                defaultextension = '.eps',
                filetypes=[
                        ('Encapsulated PostScript', '*.eps'),
                        ('PostScript', '*.ps'),
                        ('Encapsulated PostScript', '*.epi'),
                        ('All Files', '*')],
                parent = self,
                title = 'Save Figure as Encapsulated PostScript')
        if filename != '':
            self.figure.set_size_inches(
                    (self.inches_xdim.get(), self.inches_ydim.get()))
            canvas = matplotlib.backends.backend_ps.\
                    FigureCanvasPS(self.figure)
            canvas.print_eps(filename)

    def tk_save_pdf(self):
        filename = tkFileDialog.asksaveasfilename(
                defaultextension = '.pdf',
                filetypes=[
                        ('Portable Document Format', '*.pdf'),
                        ('All Files', '*')],
                parent = self,
                title = 'Save Figure as PDF')
        if filename != '':
            self.figure.set_size_inches(
                    (self.inches_xdim.get(), self.inches_ydim.get()))
            canvas = matplotlib.backends.backend_pdf.\
                    FigureCanvasPdf(self.figure)
            canvas.print_pdf(filename)

    def tk_save_img(self):
        filename = tkFileDialog.asksaveasfilename(
                defaultextension = '.png',
                filetypes = [
                        ('Any Image File Format', '*'),
                        ('All Files', '*')],
                parent = self,
                title = 'Save Figure as Image')
        if filename != '':
            canvas = matplotlayers.backends.PIL.FigureCanvasPIL(self.figure)
            image = canvas.output_PIL(
                    (self.pixels_xdim.get(), self.pixels_ydim.get()))
            image.save(filename)
