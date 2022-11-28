#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 20:41:44 2020

@author: Max Pensack
@edits: Rahim Hashim (3/3/2022)
"""
import os
import sys
import string
import matplotlib
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection

# Fixing random state for reproducibility
#np.random.seed(7311989)
radius = 100

def new_poly(initial_vertices): 

	gain = radius*.2*np.random.randn()
	new_vertices = np.empty([len(initial_vertices)*2,2])
	diffs = np.diff(initial_vertices,axis=0)
	thetas = np.empty([len(initial_vertices),1])
	
	for i in range(len(initial_vertices)):
		new_vertices[2*i] = initial_vertices[i]
		new_vertices[2*i+1] = np.mean(initial_vertices[i:i+2],axis=0)
		if i == len(initial_vertices)-1:
			thetas[i] = np.arctan(diffs[0,1]/diffs[0,0])
		else:
			thetas[i] = np.arctan(diffs[i,1]/diffs[i,0])
		
		new_vertices[2*i+1,0] = new_vertices[2*i+1,0] + gain * np.sin(thetas[i])
		new_vertices[2*i+1,1] = new_vertices[2*i+1,1] - gain * np.cos(thetas[i])
	return new_vertices


def fractal_generator():
	#Parameters
	n_layers = 4
	
	fig, ax = plt.subplots()
	patches = []
	
	#For each layer
	for i in range(n_layers):
		n_edges = np.random.randint(3,9) #initial number of edges
		recursion_depth = np.random.randint(3,6) #max # of recursive steps
		
		#Generate n-sided polygon
		initial_poly = mpatches.RegularPolygon((0,0), n_edges, radius=radius-radius*0.1*i, orientation=2*np.pi*np.random.randn())
		vertices = mpatches.Patch.get_verts(initial_poly)
		
		#Deflect midpoints
		for j in range(recursion_depth):
			vertices = new_poly(vertices)

		patches.append(mpatches.Polygon(vertices))
	
	colors = 100*np.random.rand(len(patches))
	colormap_lists = matplotlib.pyplot.colormaps()
	random_colormap_index = np.random.randint(0,len(colormap_lists))
	random_colormap = colormap_lists[random_colormap_index]
	p = PatchCollection(patches, cmap=random_colormap, alpha=0.5)
	p.set_array(colors)
	ax.add_collection(p)
	
	#Add black circle to center of image
	#ax.add_patch(mpatches.Circle((0,0), radius=0.05*radius, color='k'))
	
	plt.axis('equal')
	plt.axis('off')
	plt.tight_layout()
	return fig

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

	# Make stimuli
	for f_index in range(NUM_FRACTALS):
		filename= '_fractal_'+alphabet_string[f_index]+'.png'
		f = fractal_generator()

		# Save to current directory (for daily use)
		f.savefig(filename, facecolor=[0.5, 0.5, 0.5], dpi=radius)
		
		# Check whether the specified path exists or not
		if os.path.exists(PATH) == False:
			os.mkdir(PATH)
      replace_fractals = 'y'
    else:
      replace_fractals = input('Fractals already saved in {} folder. Replace? y/N '.format(DATE))

    if replace_fractals.lower() == 'y':
  		# Save to _fractals directory (for record keeping)
  		file_path = os.path.join(PATH, filename)
  		f.savefig(file_path, facecolor=[0.5, 0.5, 0.5], dpi=radius)
    else:
      print('Fractals in {} folder not overriden.'.format(PATH))

main()