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

# Remove grey colormaps
all_colormap = matplotlib.pyplot.colormaps()
colormaps_remove = ['Greys', 'Greys_r']
colormap_list = [elem for elem in all_colormap if elem not in colormaps_remove]

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


def hikosaka_generator():
	#Parameters
	n_layers = np.random.randint(2,5)
	
	fig, ax = plt.subplots()
	patches = []
	
	#For each layer
	for i in range(n_layers):
		n_edges = np.random.randint(3,9) #initial number of edges
		recursion_depth = np.random.randint(3,7) #max # of recursive steps
		print('  Number of Edges {} | Recursion Depth: {}'.format(n_edges, recursion_depth))
		
		#Generate n-sided polygon
		initial_poly = mpatches.RegularPolygon((0,0),
																					 n_edges,
																					 radius=radius-radius*0.1*i,
																					 orientation=2*np.pi*np.random.randn())
																					 
		vertices = mpatches.Patch.get_verts(initial_poly)
		
		#Deflect midpoints
		for j in range(recursion_depth):
			vertices = new_poly(vertices)

		patches.append(mpatches.Polygon(vertices))
	
	colors = 100*np.random.rand(len(patches))
	random_colormap_index = np.random.randint(0,len(colormap_list))
	random_colormap = colormap_list[random_colormap_index]
	# non-repeating colormaps
	colormap_list.remove(random_colormap)
	p = PatchCollection(patches, cmap=random_colormap, alpha=0.5)
	p.set_array(colors)
	ax.add_collection(p)
	
	plt.axis('equal')
	plt.axis('off')
	return fig