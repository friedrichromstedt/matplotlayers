import matplotlib.figure
import matplotlayers.stack
import matplotlayers.backends.PIL

figure = matplotlib.figure.Figure(frameon=False)
stack = matplotlayers.stack.Stack(figure)

PIL_canvas = matplotlayers.backends.PIL.FigureCanvasPIL(figure)

image = PIL_canvas.output_PIL((500, 500))

image.save('Test_PIL.png')
print "Image saved to 'Test_PIL.png'."
