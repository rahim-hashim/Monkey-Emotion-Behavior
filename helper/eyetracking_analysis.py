import os
import math 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp2d
from matplotlib.image import NonUniformImage
from collections import defaultdict, OrderedDict
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

# number of bins for 2d histogram
HIST_BINS = 10

def calc_dist(x2, x1, y2, y1):
	dist = math.hypot(x2 - x1, y2 - y1)
	return dist

def eye_delay(trial, xy_axis, session_obj):
	eye_window = session_obj.window_blink
	eye_window = 1500 # last 200 ms
	delay_end = trial['Trace End']
	eye_axis = 'eye_' + xy_axis
	eye_data = trial[eye_axis][delay_end-eye_window:delay_end]
	pupil = trial['eye_pupil'][delay_end-eye_window:delay_end]
	# eye_filtered = eye_data[pupil != 0]
	return eye_data

def print2dhist(H, xedges, yedges, ax2, label):
	defensive_eye_position = 0
	for x in range(len(xedges)-1):
		for y in range(len(yedges)-1):
			x_edge = xedges[x]
			y_edge = yedges[y]
			if label == True:
				color = 'white' if H[x][y] > 0.15 else 'black'
				ax2.text(x_edge+(HIST_BINS/2), y_edge+(HIST_BINS/2), 
								 "{:.2f}".format(H[x, y]), 
								 ha="center", va="center", size=10, color=color)
			if y == 0:
				print(x_edge, end='   ')
			# edges are left to right, bottom to top
			# i.e. x_edge, y_edge = -10, -10 -> 
			#   x from -10 to 0
			#   y from -10 to 0
			# therefore, to get only from -10 -> 10 in x and y
			# we need to be inclusive at negative ranges and exclusive at positive ranges
			if (x_edge < -10) or (y_edge < -10) or (x_edge >= 10) or (y_edge >= 10):
				defensive_eye_position += H[x][y]
	defensive_eye_percentage = defensive_eye_position*100
	print(end='\n')
	print(np.flip(H, axis=0)) # edges are -40 -> 40 but yaxis is 40 -> -40
	print('outside x,y [-10, 10]: {}%'.format(round(defensive_eye_percentage, 2)))

def eyetracking_analysis(df, session_obj, TRIAL_THRESHOLD):
	df['eye_delay_x'] = df.apply(eye_delay, xy_axis='x', session_obj=session_obj, axis=1)
	df['eye_delay_y'] = df.apply(eye_delay, xy_axis='y', session_obj=session_obj, axis=1)
	df_count = df[df['fractal_count_in_block'] > TRIAL_THRESHOLD] \
								if TRIAL_THRESHOLD else df
	axis_min = -40
	axis_max = 40
	xedges = np.linspace(axis_min, axis_max, HIST_BINS-1) # default 9 bins
	yedges = np.linspace(axis_min, axis_max, HIST_BINS-1) # default 9 bins
	for v_index, valence in enumerate(sorted(df['valence'].unique(), reverse=True)):
		df_valence = df_count[df_count['valence'] == valence]
		eye_x_delay = df_valence['eye_delay_x'].tolist()
		eye_y_delay = df_valence['eye_delay_y'].tolist()
		fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(12, 5))
		# Scatter plot
		eye_x_delay_tenth = [x[::10] for x in eye_x_delay]
		eye_y_delay_tenth = [y[::10] for y in eye_y_delay]
		ax1.scatter(s=1, x=eye_x_delay_tenth, y=eye_y_delay_tenth, 
								color=session_obj.valence_colors[valence],
								alpha=0.2)
		ax1.set_xlim(axis_min, axis_max)
		ax1.set_ylim(axis_min, axis_max)
		ax1.set_facecolor('white')
		ax1.grid(True, color='lightgrey')
		axis_range = np.arange(axis_min, axis_max+1, 10)
		ax1.set_xticks(axis_range)
		ax1.set_xticklabels(axis_range, fontsize=12)
		ax1.set_yticks(axis_range)
		ax1.set_yticklabels(axis_range, fontsize=12)
		ax1.set_title('scatter plot')
		ax1.set_xlabel('x')
		ax1.set_ylabel('y')
		# 2D histogram
		x_flatten = [item for sublist in eye_x_delay for item in sublist]
		y_flatten = [item for sublist in eye_y_delay for item in sublist]
		H, xedges, yedges = np.histogram2d(x_flatten, y_flatten,
							bins=(xedges, yedges), density=False)
		print('Total Eye Positions: {}'.format(len(x_flatten)))
		print('Histogram Positions: {}'.format(int(np.sum(H))))
		blink_rate = round((1 - np.sum(H)/len(x_flatten))*100, 2)
		H_norm = H/np.sum(H) # normalize to 1
		# cmap = plt.cm.Reds if valence < 0 else plt.cm.Blues
		cmap = plt.cm.Greys
		with np.printoptions(precision=4, suppress=True):
			print2dhist(H_norm, xedges, yedges, ax2, label=True)
		# Histogram does not follow Cartesian convention (see Notes),
		# therefore transpose H for visualization purposes. 
		H_norm = H_norm.T # see np.histogram2d documentation for details
		# ax2.imshow(H, cmap=cmap, extent=(axis_min, axis_max, axis_min, axis_max), 
		#             interpolation='spline16')
		if valence > 0 or valence < 0:
			vmin,vmax = 0.0,0.5 # to set the same colorbar for all plots
		# vmin,vmax = None,None
		im = ax2.pcolormesh(xedges, yedges, H_norm, vmin=vmin,vmax=vmax, cmap=cmap)
		ax2.set_xlabel('x')
		ax2.set_ylabel('y')
		axis_range = np.arange(axis_min, axis_max+1, 10)
		ax2.set_xticks(axis_range)
		ax2.set_xticklabels(axis_range, fontsize=12)
		ax2.set_yticks(axis_range)
		ax2.set_yticklabels(axis_range, fontsize=12)
		ax2.set_title('histogram')
		ax2.grid()
		fig.tight_layout()
		fig.colorbar(im, ax=ax2)
		print('outside x,y [-40, 40]: {}%'.format(blink_rate))
		FIGURE_SAVE_PATH = session_obj.figure_path
		fig_name = 'eye_heatmap_{}.png'.format(valence)
		img_save_path = os.path.join(FIGURE_SAVE_PATH, fig_name)
		fig.savefig(img_save_path, dpi=150, bbox_inches='tight', transparent=True)
		print('  {} saved.'.format(fig_name))
		# ax2.imshow(H, cmap=cmap, interpolation = 'nearest')