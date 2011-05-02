import Tkinter
import matplotlib.figure
import matplotlayers
import matplotlayers.backends.PIL
import matplotlayers.backends.tk
import numpy

matplotlayers.backends.tk.has_mainloop = True

figure = matplotlib.figure.Figure(frameon=False)
stack = matplotlayers.Stack(figure)

tk = Tkinter.Tk()
tk_canvas = matplotlayers.backends.tk.FigureCanvasTk(tk, figure)

stack_canvas = matplotlayers.backends.StackCanvas(stack)
tk_canvas.register(stack_canvas)

x = numpy.arange(0, 100)
plot_layer = matplotlayers.LayerPlot(
        x=x, y=numpy.sin(x * 0.1))
stack.add_layer(plot_layer)
stack.render()
tk_canvas.update()

tk.mainloop()
