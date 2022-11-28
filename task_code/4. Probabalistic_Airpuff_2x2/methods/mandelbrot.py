import numpy as np
import matplotlib
import warnings
import matplotlib.pyplot as plt
import PIL
from PIL import ImageChops

# Remove grey colormaps
all_colormap = matplotlib.pyplot.colormaps()
colormaps_remove = ['Greys', 'Greys_r']
colormap_list = [elem for elem in all_colormap if elem not in colormaps_remove]

radius = 100

def plot_mandelbrot(x, X, y, Y):
	delta = (X-x)/300
	re, im = np.mgrid[x:X:delta, y:Y:delta]
	c = (re + 1j*im).reshape(im.shape[0], -1).T

	z = np.zeros_like(c)
	escape = np.zeros_like(np.absolute(c))
	for i in range(100):
		z = z*z + c # mandelbrot eqn
		#z = z/((np.e**z) + c) # mandelbrot eqn
		#z = 1/(z+c**3) # mandelbrot eqn
    #z = 1/(z+c**3) # mandelbrot eqn
		idx = (np.absolute(z) > 4) & (escape == 0)
		escape[idx]  = i
	
	random_colormap_index = np.random.randint(0,len(colormap_list))
	random_colormap = colormap_list[random_colormap_index]

	plt.imshow(escape, extent=(x,X,y,Y), cmap=random_colormap)

def plot_mandelbrot_at(x, y, D):
	return plot_mandelbrot(x-D, x+D, y-D, y+D)

def mandelbrot_generator():
	fig, ax = plt.subplots()

	x_sign = 1 if np.random.random() < 0.5 else -1
	y_sign = 1 if np.random.random() < 0.5 else -1
	x, y, D = [np.random.rand()*x_sign,
			   np.random.rand()*y_sign,
			   np.random.rand()]

	print('  x: {}\n  y:  {}\n  D:  {}'.format(x, y, D))
	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		#plot_mandelbrot_at(-.75, -.25, .1)
		plot_mandelbrot_at(x, y, .4)

	plt.axis('equal')
	plt.axis('off')
	return fig
	# image = PIL.Image.frombytes('RGB', 
	# 	fig.canvas.get_width_height(),fig.canvas.tostring_rgb())
	# if not ImageChops.invert(image).getbbox():
	# 	return fig
	# else:
	# 	plt.close()
	# 	fig, ax = plt.subplots()
	# 	mandelbrot_generator()