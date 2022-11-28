import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from collections import defaultdict
from scipy.interpolate import make_interp_spline, BSpline

def moving_avg(data, N):
	'''
	moving_avg calculates the moving avg
	given window N
	'''
	cumsum_vec = np.cumsum(np.insert(data, 0, 0))
	ma_vec = (cumsum_vec[N:] - cumsum_vec[:-N]) / N
	return np.array(ma_vec)

def moving_var(data, N):
	'''
	moving_avg calculates the moving variance
	given window N
	'''
	mv_vec = []
	data_vec = np.insert(data, 0, 0)
	for i in range(len(data_vec[N:])):
		mv_vec.append(np.std(data_vec[i:i+N]))
	return np.array(mv_vec)

def smooth_plot(x, y):
  '''
  smooth_plot smoothens any 2D line (i.e. plt.plot)
  using scipy's BSpline function
  '''
  xnew = np.linspace(x.min(), x.max(), 300) 
  spl = make_interp_spline(x, y, k=2)  # type: BSpline
  power_smooth = spl(xnew)
  return xnew, power_smooth

def round_up_to_odd(f):
  return np.ceil(f) // 2 * 2 + 1

def sankey_plot(df, error_dict):
	# Sankey Plot
	label = []
	source = []
	target = []
	value = []
	CONDITIONS = [1, 2]
	if 1 in CONDITIONS:
		label.append('Instructed')
	if 2 in CONDITIONS:
		label.append('Uninstructed')
	for k_index, key in enumerate(list(range(10))):
		for c_index, condition in enumerate(CONDITIONS):
			outcome_key = [key]
			num_trials = df.loc[(df['error_type'].isin(outcome_key) &\
																df['condition'].isin([condition]))]
			source.append(c_index)
			target.append(k_index+len(CONDITIONS))
			value.append(len(num_trials))

	label += ['Correct'] + list(error_dict.values())
	# data to dict, dict to sankey
	link = dict(source = source, target = target, value = value)
	node = dict(label = label, pad=20, thickness=5)
	data = go.Sankey(link = link, node=node)
	# plot
	sankey_fig = go.Figure(data)
	return sankey_fig

def set_plot_params(FONT, AXES_TITLE, AXES_LABEL, TICK_LABEL, LEGEND, TITLE) -> None:
	'''
	set_plot_params sets the plot parameters
	'''
	plt.rc('font', size=FONT)          			# controls default text sizes
	plt.rc('axes', titlesize=AXES_TITLE)    # fontsize of the axes title
	plt.rc('axes', labelsize=AXES_LABEL)    # fontsize of the x and y labels
	plt.rc('xtick', labelsize=TICK_LABEL)   # fontsize of the tick labels
	plt.rc('ytick', labelsize=TICK_LABEL)   # fontsize of the tick labels
	plt.rc('legend', fontsize=LEGEND)    		# legend fontsize
	plt.rc('figure', titlesize=TITLE)  			# fontsize of the figure title