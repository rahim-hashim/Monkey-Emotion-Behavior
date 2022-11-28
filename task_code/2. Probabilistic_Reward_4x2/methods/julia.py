import matplotlib
import numpy as np
import matplotlib.pyplot as plt

UNIFORM_THRESHOLD = 0.7
# Remove grey colormaps
all_colormap = matplotlib.pyplot.colormaps()
colormaps_remove = ['Greys', 'Greys_r']
colormap_list = [elem for elem in all_colormap if elem not in colormaps_remove]

def julia_set(c, max_iterations, x, y, zoom, height, width):
	# To make navigation easier we calculate these values
	x_width = 1.5
	y_height = 1.5*height/width
	x_from = x - x_width/zoom
	x_to = x + x_width/zoom
	y_from = y - y_height/zoom
	y_to = y + y_height/zoom
	# Here the actual algorithm starts
	x = np.linspace(x_from, x_to, width).reshape((1, width))
	y = np.linspace(y_from, y_to, height).reshape((height, 1))
	#z = x + 1j * y
	z = x + 1j * y
	# Initialize z to all zero
	c = np.full(z.shape, c)
	# To keep track in which iteration the point diverged
	div_time = np.zeros(z.shape, dtype=int)
	# To keep track on which points did not converge so far
	m = np.full(c.shape, True, dtype=bool)
	for i in range(max_iterations):
			z[m] = z[m]**2 + c[m]
			m[np.abs(z) > 2] = False
			div_time[m] = i
	return div_time

def julia_generator():

	fig, ax = plt.subplots()

	non_black = True
	num_iterations = 0
	while (non_black):
		zoom = np.random.randint(0,100)
		x = np.random.rand()
		y = np.random.rand()
		height = 1000
		width = 1000
		print('  Iteration: {}'.format(num_iterations)); num_iterations += 1
		print('    X: {} | Y: {} | Zoom: {}'.format(x, y, zoom))
		im_matrix = julia_set(-0.8+0.156j, 512, x, y, zoom, height, width)
		#im_matrix = julia_set(0.285+0.01j, 512, x, y, zoom, height, width)
		flatten_div = im_matrix.flatten() 
		count_arr = np.bincount(flatten_div)
		val_most_common = count_arr.argmax()
		count_most_common = count_arr[val_most_common]
		uniform_perc = round(count_most_common/(height*width)*100, 2)
		print('    Uniform Val: {} | Uniform Percent: {}%'.format(val_most_common, uniform_perc))
		# UNIFORM_THRESHOLD sets max uniformity of the image
		if count_most_common >= height*width*UNIFORM_THRESHOLD: 
			continue
		else:
			non_black = False
	#im_matrix = julia_set(c=-0.8+0.156j, max_iterations=512)
	# plt.imshow(julia_set(c=-0.7269 + 0.1889j, max_iterations=256), cmap='magma')
	random_colormap_index = np.random.randint(0,len(colormap_list))
	random_colormap = colormap_list[random_colormap_index]
	plt.imshow(im_matrix, cmap=random_colormap)
	plt.axis('equal')
	plt.axis('off')
	return fig