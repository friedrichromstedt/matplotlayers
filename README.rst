Short Introduction
==================

Rationale
---------

``matplotlayers`` uses a layered, object-oriented approach on top of the
matplotlib API.  When using matplotlayers, you can no longer reliably use the
matplotlib API, but only the matplotlayers API.  This comes with the following
advantages:

*   Change the data of a layer, and update the plot.  Axes settings will be
    preserved (as long as they are known to matplotlayers).
*   Add *and remove* layers from a Stack (a Stack is the matplotlayers
    equivalent of a matplotlib Axes).
*   Automatically update Colorbars, once they're connected to the layer
    they originate from.
*   Layers can be in as many stacks as you want.  What you can learn from
    this is, that there are no cyclic references in matplotlayers.
*   Create PIL (i.e., raster image) backends, which render your figure
    directly into a rasterised PIL image.  Or create a Tkinter backend, to
    display the Figure on screen, modify the titles and labels interactively,
    zoom with mouse gestures, and save the Figure as raster image, EPS, or 
    PDF.
*   Embed matplotlib into Tkinter applications or offline applications using
    the above advatages.

It also has disadvantages:

*   You cannot use the full matplotlayers API, but only those I wrote 
    implementation in matplotlayers style for.  Many plot commands are 
    supported, though, including the pcolor et al., and ordinary plot
    commands.  *Not* supported are e.g. legends (!).
*   You have to learn the matplotlayers API.  This also means, you cannot use
    the pylab MATLAB-like matplotlib interface anymore.  Your code might turn
    out to be slightly more long, because you have to be more explicit in what
    you want.

Plotting Example
----------------

::

    import matplotlib.figure
    import matplotlayers

    figure = matplotlib.figure.Figure(frameon=False)
    stack = matplotlayers.Stack(figure)
    layer = matplotlayers.LayerPlot(x=[0, 1, 2], y=[0, 3, 2])
    stack.add_layer(layer)

    stack.render()

To actually output the figure, you need to create a backend.  The backend
transforms the figure into some output format, just as in matplotlib::

    [continuation]

    import matplotlib.backends.backend_pdf

    backend = matplotlib.backends.backend_pdf.FigureCanvasPdf(figure)
    backend.print_pdf('YourPDF.pdf')

You might also want to use the backends which come with matplotlayers, and
which aren't included in matplotlib::

    [continuation]

    import matplotlayers.backends.tk
    import Tkinter

    tk = Tkinter.Tk()
    backend_tk = matplotlayers.backends.tk.FigureCanvasTk(tk, figure)

    - or -

    import matplotlayers.backends.PIL

    backend = matplotlayers.backends.PIL.FigureCanvasPIL(figure)
    image = backend.output_PIL(shape=(800, 600))

    image.save('YourRasterImage.png')

For the Tkinter backend, you might do create handlers which enable you to 
zoom and modify the axes::
    
    [continuation]

    canvas = matplotlayers.backends.StackCanvas(stack)
    backend_tk.register(canvas)

You can zoom and pan as many Stacks on the Figure as you want.

Layer Usage
-----------

The layers use a keyword configuration system.  Let's create a Layer first::

    layer = matplotlayers.LayerPlot()

Now change its configuration (the layer will not plot anything until it's 
properly configured)::

    layer.configure(x=[0, 1, 2])
    layer['y'] = [0, 3, 2]

Let's turn it into non-plotting again::

    layer.unconfigure(x)

Especially the not-fully-configured state can prove extremely useful for
programming embedded Tkinter matplotlayers applications.

This is just a tutorial, so all the special keyword configurations are not
explained here.  For standard configurations, just use those keywords you
would use in matplotlib.  So if you would do in matplotlib::

    axes.plot([0, 1, 2], [0, 3, 2], fmt='ok')

you can do this in matplotlayers quite the same::

    layer = matplotlayers.LayerPlot(x=[0, 1, 2], y=[0, 3, 2], fmt='ok')

You can configure the keywords using initialisation arguments, 
``.configure()``, ``.unconfigure()``, or the slicing operator syntax.

Tkinter Usage
-------------

*   Click left onto an Axes and drag to zoom (try it!)
*   Click right onto an Axes and drag to pan.
*   Double-click onto a Figure to open the Save-As-Dialog
*   Double-right-click onto an Axes to open the Axes modification dialogue
    (title, labels, limits, autoscaling).

When using matplotlayers in a mainloop() application, make sure you do the
following somewhere::
    
    import maptlotlayers.backends.tk

    matplotlayers.backends.tk.has_mainloop = True

Otherwise your application might bisbehave in slight to strong ways or might
even crash or hang.  This is due to some Tkinter restrictions.

Installation
============

matplotlayers uses `Bento <http://github.com/cournape/Bento>`_ as its 
packaging solution.  Please use Bento for installing matplotlayers.

You further need `keyconf <http://github.com/friedrichromstedt/keyconf>`_ to
use matplotlayers.  ``keyconf`` supplies the keyword configuration framework.
