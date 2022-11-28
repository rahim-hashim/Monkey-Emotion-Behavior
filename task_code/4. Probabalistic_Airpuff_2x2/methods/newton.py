'''
Adapted from: https://computingskillset.com/solving-equations/newton-fractals-explained-examples-and-python-code/
'''
import warnings
import numpy as np
import matplotlib.pyplot as plt

np.seterr(invalid='ignore')
warnings.filterwarnings('ignore')

# Remove grey colormaps
all_colormap = plt.colormaps()
colormaps_remove = ['Greys', 'Greys_r']
colormap_list = [elem for elem in all_colormap if elem not in colormaps_remove]

# initialize a dictionary of list of the roots
rootlist = {}
# function definitions to evaluate f/f' at x. Add your own as needed.
# each function definition must include a list of the roots of this function
# root list can be in any order and restricted to finite number
# example 1: polynomial function with four roots
def npe1(x):
		return (x**2-1)*(x**2+1)/(2*x*(x**2-1)+2*x*(x**2+1))
rootlist['npe1'] = [-1, 1, -1j, 1j]
# example 2: function with three roots on the unit circle
def npe2(x):
		return (x**3-1)/(3*x**2)
rootlist['npe2'] = [-.5-0.8660254037844386j,-.5+0.8660254037844386j, 1]
# example 2: function with twelve roots on the unit circle
def npe3(x):
		return (x**12-1)/(12*x**11)
rootlist['npe3'] = [-.5-0.8660254037844386j,-.5+0.8660254037844386j,.5-0.8660254037844386j,.5+0.8660254037844386j,-.5j-0.8660254037844386,-.5j+0.8660254037844386,.5j-0.8660254037844386,.5j+0.8660254037844386, 1,-1,1.j,-1.j]
# example 4 : sine function (root 0)
def npe4(x):
		return np.sin(x)
rootlist['npe4'] = [0]
# example 5: sine function (root pi)
def npe5(x):
		return np.sin(x)
rootlist['npe5'] = [np.pi]
# example 6: cos function (root pi)
def npe5(x):
		return np.cos(x)
rootlist['npe6'] = [np.pi]
# example 7: function with four roots, all real
def npe7(x):
		return (x+2.)*(x+1.5)*(x-0.5)*(x-2.)/((x+1.5)*(x-0.5)*(x-2.) + (x+2.)*(x-0.5)*(x-2.) +(x+2.)*(x+1.5)*(x-2.) + (x+2.)*(x+1.5)*(x-0.5)) 
rootlist['npe7'] = [-2, -1.5, 0.5, 2]
# example 8: cos function (root 0)
def npe8(x):
		return np.cos(x)
rootlist['npe8'] = [0]
# example 9: function with four roots, one multiple
def npe9(x):
		return (x+2)*(x+1.5)**2*(x-0.5)*(x-2)/((x+1.5)**2*(x-0.5)*(x-2) + 2*(x+2)*(x+1.5)*(x-0.5)*(x-2) +(x+2)*(x+1.5)**2*(x-2) + (x+2)*(x+1.5)**2*(x-0.5) )
rootlist['npe9'] = [-2, -1.5, 0.5, 2]
# example 10: sine function
def npe10(x):
		return np.tan(x)
rootlist['npe10'] = [0]
for i in range(1,10):
		rootlist['npe10'].extend([i*np.pi,-i*np.pi])
# define a function that can id a root from the rootlist
def id_root(zl,rlist):
		findgoal = 1.e-10 * np.ones(len(zl))
		rootid = -1 * np.ones(len(zl))
		for r in rlist:
				# check for closeness to each root in the list
				rootid = np.where(np.abs(zl-r* np.ones(len(zl))) < findgoal, np.ones(len(zl)) * rlist.index(r), rootid)
						
		return rootid

def plot_newton_fractal(func_string, xvals, yvals, num_x, num_y, perfom_shading=False):

		# set desired precision and max number of iterations
		# keep precision goal smaller than findgoal (root matching) above
		prec_goal = 1.e-11
		# max number of iterations. Is being used in a vectorized way. 
		# 50 is a good minimal value, sometimes you need 500 or more
		nmax = 200
		
		# create complex list of points from x and y values
		zlist = []
		for x in xvals:
				for y in yvals:
						zlist.append(x + 1j*y)
		
		# initialize the arrays for results, differences, loop counters  
		reslist = np.array(zlist)
		reldiff = np.ones(len(reslist))
		counter = np.zeros(len(reslist)).astype(int)
		# initialize overall counter for controlling the while loop
		overallcounter = 0
		# vectorize the precision goal
		prec_goal_list = np.ones(len(reslist)) * prec_goal
		# iterate while precision goal is not met - vectorized
		while np.any(reldiff) > prec_goal and overallcounter < nmax:
				
				# call function as defined above and 
				# compute iteration step, new x_i, and relative difference
				diff = eval(func_string+'(reslist)')
				z1list = reslist - diff
				reldiff = np.abs(diff/reslist)
				
				# reset the iteration
				reslist = z1list
				
				# increase the vectorized counter at each point, or not (if converged)
				counter = counter + np.greater(reldiff, prec_goal_list )
				# increase the control counter
				overallcounter += 1
		
		# get the converged roots matched up with those predefined in the root list
		nroot = id_root(z1list,rootlist[func_string]).astype(int)
		
		# add information about number of iterations to the rood id for shaded plotting
		if perfom_shading == True:
				nroot = nroot - 0.99*np.log(counter/np.max(counter))
		# uncomment those in case of doubt
#    print(reslist)
#    print(counter)
#    print(nroot)
		
		# get the data into the proper shape for plotting with matplotlib.pyplot.matshow
		nroot_contour = np.transpose(np.reshape(nroot,(num_x,num_y)))
				
		# create an imshow plot 
		fig, ax = plt.subplots()
		
		# plots the matrix of data in the current figure. Interpolation isn't wanted here.
		# Change color map (cmap) for various nice looks of your fractal
		random_colormap_index = np.random.randint(0,len(colormap_list))
		random_colormap = colormap_list[random_colormap_index]
		plt.imshow(nroot_contour, cmap=random_colormap)
		
		plt.axis('equal')
		plt.axis('off')
		
		# save a file of you plot. 200 dpi is good to match 1000 plot points. 
		# Increasing dpi produces more pixels, but not more plotting points.
		# Number of plotting points and pixels are best matched by inspection.
		return fig

def newton_generator():
	# define left and right boundaries for plotting    
	# for overview plots:
	interval_left = -2.1
	interval_right = 2.1
	interval_down = -2.1
	interval_up = 2.1
	# for detailed plots (adjust as needed):
	rand_float_left_right = np.random.uniform(0, 5)
	rand_float_up_down = np.random.uniform(0, 5)
	interval_left = -1 * rand_float_left_right
	interval_right = rand_float_left_right
	interval_down = -1 * rand_float_up_down
	interval_up = rand_float_up_down
	# set number of grid points on x and y axes for plotting 
	# use 100 for testing plotting ranges, 1000 for nice plots and 2000 for nicer plots
	num_x = 1000
	num_y = 1000
	# define x and y grids of points for computation and plotting the fractal
	xvals = np.linspace(interval_left, interval_right, num=num_x)
	yvals = np.linspace(interval_down, interval_up, num=num_y)
	# call the solution function for func of your choice
	# also, switch shading via number of iterations on or off
	npe_selected = 'npe'+str(np.random.randint(1,11))
	print('  npe selected: {}'.format(npe_selected))
	print('  Intervals: Left/Right {} | Up/down {}'.format(round(rand_float_left_right,2), round(rand_float_up_down,2)))
	fig = plot_newton_fractal('npe5', xvals, yvals, num_x, num_y, perfom_shading=True)
	return fig