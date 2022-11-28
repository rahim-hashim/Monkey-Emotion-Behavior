import os
import sys
import string
import random
import matplotlib
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection

# custom random fractal generators using different methods
from methods import mandelbrot, hikosaka, julia, newton

# Fixing random state for reproducibility
#np.random.seed(7311989)
radius = 100

# Remove grey colormaps
all_colormap = matplotlib.pyplot.colormaps()
colormaps_remove = ['Greys', 'Greys_r']
colormap_list = [elem for elem in all_colormap if elem not in colormaps_remove]

def main():

	fractal_num_input = input('How many fractals? ')
	try:
		NUM_FRACTALS = int(fractal_num_input)
	except:
		sys.exit('Number of fractals needs to be an integer.')

	FRACTAL_PATH = '_fractals'
	if os.path.exists(FRACTAL_PATH) == False:
		os.mkdir(FRACTAL_PATH)

	alphabet_string = string.ascii_uppercase
	DATE = datetime.today().strftime('%Y%m%d')
	PATH = os.path.join(FRACTAL_PATH, DATE)

	list_indices = np.arange(NUM_FRACTALS) + 1 # get rid of 0
	random.shuffle(list_indices)
	print('Method Order: {}'.format(list_indices))
	for f_index in range(NUM_FRACTALS):
		filename= '_fractal_'+alphabet_string[f_index]+'.png'

		random_generator = list_indices[0]

		method = ''
		if random_generator%4 == 0:				# multiple of 4
			print('Fractal {} - Newton Method'.format(f_index+1))    
			f = newton.newton_generator()
		elif random_generator%3 == 0: 		# multiple of 3
			print('Fractal {} - Julia Method'.format(f_index+1))			
			f = julia.julia_generator()
		elif random_generator%2 == 0:			# multiple of 2 (and not 4)
			print('Fractal {} - Mandelbrot Method'.format(f_index+1))			
			f = mandelbrot.mandelbrot_generator()
		elif random_generator%2 == 1:			# multiple of 1 (odd and not multiple of 3)
			print('Fractal {} - Hikosaka Method'.format(f_index+1))			
			f = hikosaka.hikosaka_generator()
		list_indices = list_indices[1:]

		# Save to current directory (for daily use)
		f.savefig(filename, facecolor=[0.5, 0.5, 0.5], dpi=radius)
		
		# Check whether the specified path exists or not
		if os.path.exists(PATH) == False:
			os.mkdir(PATH)
			replace_fractals = 'y'
		else:
			list_files = os.listdir(PATH)
			if filename in list_files:
				replace_fractals = input('Fractals already saved in {} folder. Replace? y/N '.format(DATE))
			else:
				replace_fractals = 'y'

		if replace_fractals.lower() == 'y':
			# Save to _fractals directory (for record keeping)
			file_path = os.path.join(PATH, filename)
			f.savefig(file_path, facecolor=[0.5, 0.5, 0.5], dpi=radius)
		else:
		 print('Fractals in {} folder not overriden.'.format(PATH))

main()