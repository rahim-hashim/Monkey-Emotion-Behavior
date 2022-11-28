import os
import numpy as np
import seaborn as sns
from scipy import stats
from decimal import Decimal
from matplotlib import pyplot as plt
from sklearn.neighbors import KernelDensity
from itertools import combinations, permutations

from two_sample_test import generate_data_dict

def ks_test(df, session_obj):
	"""
	calculates the ks test for the two distributions

	Args:
		df (dataframe): dataframe containing the data
		session_obj (object): session object

	Returns:
		None
	"""
	LABELS = list(session_obj.valence_labels.values())
	num_valences = len(df['valence'].unique())
	lick_prob, blink_prob, lick_dur, blink_dur = \
				generate_data_dict(df, session_obj)
	valence_combinations = list(combinations(range(num_valences), 2))
	measure_data = [lick_dur, blink_dur]
	measure_labels = ['Lick', 'Blink']
	for m_index, m_label in enumerate(measure_labels):
		prob_combinations = list(combinations(measure_data[m_index].values(), 2))
		print(m_label)
		for f_index, valence in enumerate(valence_combinations):
			prob = prob_combinations[f_index]
			ks_stat, p_val = stats.ks_2samp(prob[0], prob[1])
			valence_1, valence_2 = LABELS[valence[0]], LABELS[valence[1]]
			ks_string = round(ks_stat, 2)
			p_val_string = '%.2E' % Decimal(p_val)
			print('  {} vs {}: ks_stat: {}, p_val: {}'.format(valence_1, valence_2, ks_string, p_val_string))

def measure_hist(df, session_obj):
	"""
	plots the histograms and cdf for lick and blink duration

	Args:
		df (dataframe): dataframe containing the data
		session_obj (object): session object
	"""
	valence_list = sorted(df['valence'].unique(), reverse=True)
	# kde plot
	f1, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), 
																sharex=True,
																sharey=True)
	# cde plot
	f2, (ax3, ax4) = plt.subplots(1, 2, figsize=(10, 5),
																sharex=True,
																sharey=True)
	# histogram plot
	# f3, (ax5, ax6) = plt.subplots(1, 2, figsize=(10, 5))
	COLORS = session_obj.valence_colors
	LABELS = session_obj.valence_labels
	FIGURE_SAVE_PATH = session_obj.figure_path
	x = np.arange(0, 1.2, 0.2)
	x_label = [round(x*100) for x in x]
	for v_index, valence in enumerate(valence_list):
		df_valence = df[df['valence'] == valence]
		# lick
		lick_data = np.array(df_valence['lick_duration'])/5 # normalize data
		sns.kdeplot(ax=ax1,
								data=lick_data,  
								color=COLORS[v_index], 
								label=LABELS[valence],
								fill=True,
								linewidth=2,
								cut=0)
		sns.ecdfplot(ax=ax3,
								 data=lick_data,
								 color=COLORS[v_index],
								 label=LABELS[valence],
								 linewidth=2)
		# ax5.hist(lick_data, histtype='barstacked', alpha=0.5, bins=20, 
		# 				 color=COLORS[v_index], label=LABELS[valence])
		# blink
		blink_data = np.array(df_valence['blink_duration_offscreen'])
		sns.kdeplot(ax=ax2,
								data=df_valence,
								x='blink_duration_offscreen',  
								color=COLORS[v_index], 
								label=LABELS[valence],
								fill=True,
								linewidth=2,
								cut=0)
		sns.ecdfplot(ax=ax4,
								 data=df_valence,
								 x='blink_duration_offscreen',
								 color=COLORS[v_index],
								 label=LABELS[valence],
								 linewidth=2)
		# ax6.hist(blink_data, histtype='bar', alpha=0.5, bins=20, 
		# 				 color=COLORS[v_index], label=LABELS[valence])
	ax1.set_xticks(x)
	ax1.set_xticklabels(x_label)
	ax1.set_xlabel('Percent of Trial Licking', fontsize=16)
	ax1.set_ylabel('Density', fontsize=16)
	ax2.set_xlabel('Percent of Trial Blinking', fontsize=16)
	ax1.legend(loc='upper left')
	ax2.legend(loc='upper right')
	# set facecolor to black:
	f1.set_facecolor("k")
	params = {"ytick.color" : "w",
						"xtick.color" : "w",
						"axes.labelcolor" : "w",
						"axes.edgecolor" : "w",
						"axes.titlecolor" : "w"}
	plt.rcParams.update(params)
	img_save_path = os.path.join(FIGURE_SAVE_PATH, 'lick_blink_hist')
	f1.savefig(img_save_path, dpi=150)
	print('  lick_blink_hist.png saved.')

	ax3.set_xticks(x)
	ax3.set_xticklabels(x_label)
	ax3.set_xlabel('Percent of Trial Licking', fontsize=16)
	ax3.set_ylabel('Proportion', fontsize=16)
	ax4.set_xlabel('Percent of Trial Blinking', fontsize=16)
	ax3.legend(loc='upper left')
	ax4.legend(loc='lower right')
	# set facecolor to black:
	f2.set_facecolor("k")
	params = {"ytick.color" : "w",
						"xtick.color" : "w",
						"axes.labelcolor" : "w",
						"axes.edgecolor" : "w",
						"axes.titlecolor" : "w"}
	plt.rcParams.update(params)
	img_save_path = os.path.join(FIGURE_SAVE_PATH, 'lick_blink_cdf')
	f2.savefig(img_save_path, dpi=150)
	print('  lick_blink_cdf.png saved.')
	ks_test(df, session_obj)