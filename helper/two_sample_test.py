import os
import math
import string
import numpy as np
import pandas as pd
from scipy import signal
from decimal import Decimal
import matplotlib.pyplot as plt
from collections import defaultdict
from itertools import combinations, permutations
from scipy.stats import ttest_ind, ttest_ind_from_stats
import warnings
warnings.filterwarnings("ignore")

# Custom Functions
from plot_helper import smooth_plot, round_up_to_odd, moving_avg, moving_var, set_plot_params

def generate_data_dict(session_df, session_obj):

	lick_data_probability = defaultdict(list)
	blink_data_probability = defaultdict(list)
	lick_data_duration = defaultdict(list)
	blink_data_duration = defaultdict(list)

	PRE_CS = 50 # time before CS-on (for moving average calculation)
	FIGURE_SAVE_PATH = session_obj.figure_path
	COLORS = session_obj.colors
	WINDOW_THRESHOLD_LICK = session_obj.window_lick
	
	valence_list = sorted(session_df['valence'].unique(), reverse=True)
	for df_index, valence in enumerate(valence_list):

		df = session_df[session_df['valence'] == valence]

		# valence-specific session lick/blink data
		lick_data_raster = df['lick_raster'].tolist()
		blink_data_raster = df['blink_raster'].tolist()
		# pupil_data = df['eye_pupil'].tolist()

		# single bin lick data (-<WINDOW_THRESHOLD>ms from trace interval end)

		for t_index, trial in enumerate(lick_data_raster):
		
			trace_off_time = df['Trace End'].iloc[t_index]
			# Lick/Blink Probability
			## counts if there was any lick in the specified time window
			lick_data_window = df['lick_count_window'].iloc[t_index]
			if 1 in lick_data_window:
				lick_data_probability[df_index].append(1)
			else:
				lick_data_probability[df_index].append(0)

			## counts if there was any blink in the specified time window
			blink_data_window = df['blink_count_window'].iloc[t_index]
			if 1 in blink_data_window:
				blink_data_probability[df_index].append(1)
			else:
				blink_data_probability[df_index].append(0)

			# Lick/Blink Duration
			lick_raw = df['lick'].iloc[t_index]
			lick_data_voltage = lick_raw[trace_off_time-WINDOW_THRESHOLD_LICK:trace_off_time]
			lick_data_voltage_mean = np.mean(lick_data_voltage)
			lick_data_duration[df_index].append(lick_data_voltage_mean)

			blink_raw = df['blink_duration_offscreen'].iloc[t_index]
			blink_data_duration[df_index].append(blink_raw)
	
	return lick_data_probability, blink_data_probability, lick_data_duration, blink_data_duration

def two_sample_test(data_type, data_raster, condition, session_obj, direction='forwards'):
	'''Lick/Blink Probability 2-Sample T-Test'''

	f, axarr = plt.subplots(2,3, figsize=(12,4), sharex=True, sharey=True)

	FIGURE_SAVE_PATH = session_obj.figure_path
	COLORS = list(session_obj.valence_colors.values())
	LABELS = list(session_obj.valence_labels.values())[:4]
	num_valences = len(LABELS)
	window_width = 5

	verbose = False
	valence_combinations = list(combinations(range(num_valences), 2))
	prob_combinations = list(combinations(data_raster.values(), 2))
	for f_index, valence in enumerate(valence_combinations):
		if valence == (0, 1):
			ax = axarr[0][0]
		if valence == (0, 2):
			ax = axarr[0][1]
		if valence == (0, 3):
			ax = axarr[0][2]
		if valence == (1, 2):
			ax = axarr[1][0]
		if valence == (1, 3):
			ax = axarr[1][1]
		if valence == (2, 3):
			ax = axarr[1][2]
		valence_1, valence_2 = LABELS[valence[0]], LABELS[valence[1]]
		a = prob_combinations[f_index][0]
		d = prob_combinations[f_index][1]
		t_all, p_all = ttest_ind(a, d, equal_var=False)
		ma_vec_a = moving_avg(a, window_width)
		mv_vec_a = moving_var(a, window_width)
		ma_vec_d = moving_avg(d, window_width)
		mv_vec_d = moving_var(d, window_width)
		min_array, max_array = (ma_vec_a, ma_vec_d) if len(a) <= len(d) else (ma_vec_d, ma_vec_a)
		min_len = len(min_array)
		one_star_flag = 1
		two_star_flag = 1
		three_star_flag = 1
		if direction == 'backwards':
			# do something
			pass
		if direction == 'forwards':
			for window in range(window_width, min_len):
				a_windowback = a[window-window_width:window]
				d_windowback = d[window-window_width:window]
				t, p = ttest_ind(a_windowback, 
												d_windowback,
												equal_var=False)
				star_pos = max(np.mean(a_windowback),np.mean(d_windowback))+0.05
				if p < 0.001 and three_star_flag:
					ax.text(window-window_width, star_pos, s='***', ha='center')
					p_str = "{:.2e}".format(p)
					one_star_flag = 0
					two_star_flag = 0
					three_star_flag = 0	
				elif p < 0.01 and two_star_flag:
					ax.text(window-window_width, star_pos, s='**', ha='center')
					p_str = "{:.2e}".format(p)	
					one_star_flag = 0
					two_star_flag = 0	
				elif p < 0.05 and one_star_flag:
					p_str = str(round(p, 3))
					ax.text(window-window_width, star_pos, s='*', ha='center')
					one_star_flag = 0
				else:
					p_str = str(round(p, 3))
			# Plot Running Average
			ax.plot(list(range(len(ma_vec_a))), ma_vec_a, c=COLORS[valence[0]], lw=4, label=valence_1)
			ax.plot(list(range(len(ma_vec_d))), ma_vec_d, c=COLORS[valence[1]], lw=4, label=valence_2)
			# Plot Variance 
			ax.fill_between(list(range(len(ma_vec_a))), ma_vec_a-(mv_vec_a/2), ma_vec_a+(mv_vec_a/2),
											color=COLORS[valence[0]], alpha=0.2) # variance
			ax.fill_between(list(range(len(ma_vec_d))), ma_vec_d-(mv_vec_d/2), ma_vec_d+(mv_vec_d/2),
											color=COLORS[valence[1]], alpha=0.2) # variance
			ax.set_xticks(list(range(0, len(ma_vec_a), 5)))
			ax.set_xticklabels(list(range(window_width, len(ma_vec_a)+window_width, 5)))
		if direction == 'backwards':
			size_diff = len(max_array) - len(min_array)
			for window in range(window_width, min_len):
				min_windowback = min_array[window-window_width+size_diff:window+size_diff]
				max_windowback = max_array[window-window_width:window]
			# Plot Running Average
			ax.plot(list(range((min_len-1)*-1, 1)), ma_vec_a[-min_len:], c=COLORS[valence[0]], lw=4, label=valence_1)
			ax.plot(list(range((min_len-1)*-1, 1)), ma_vec_d[-min_len:], c=COLORS[valence[1]], lw=4, label=valence_2)
			base = 5
			round_off = base * math.ceil((min_len-1)/ base)
			ax.set_xticks(list(range((round_off)*-1, 1, 5)))
			ax.set_xticklabels(list(range((round_off)*-1, 1, 5)))
		ax.legend(fontsize='x-small', loc='lower left')
		if 'prob' in data_type:
			ax.set_ylim([0,1])
		if verbose:
			print('  {}'.format(window),
						valence_1, valence_2, 
						round(np.mean(a), 3),
						round(np.mean(d), 3),
						format(p_all, '.3g'))

	f.supylabel('Moving Avg ({} Trials)'.format(window_width))
	if direction=='backwards':
		if condition == 1:
			f.supxlabel('Trial Number Before Switch')
		else:
			f.supxlabel('Trial Number Before Session End')
	else:
		f.supxlabel('Trial Number')
	title = data_type.split('-')
	title_full = ' '.join(title)
	f.suptitle(title_full.title() + ' (Condition {})'.format(condition))

	f.tight_layout()
	img_save_path = os.path.join(FIGURE_SAVE_PATH, 't_test_{}_{}.png'.format(data_type, condition))
	f.savefig(img_save_path, dpi=150, bbox_inches='tight', pad_inches = 0.1)
	plt.close('all')

def t_test_moving_avg(df, session_obj, condition):
	# T-Test Plots
	lick_data_probability, blink_data_probability, lick_data_duration, blink_data_duration = generate_data_dict(df, session_obj)
	set_plot_params(FONT=10, AXES_TITLE=11, AXES_LABEL=10, TICK_LABEL=10, LEGEND=8, TITLE=14)
	two_sample_test('lick-duration', lick_data_duration, condition, session_obj)
	two_sample_test('blink-duration', blink_data_duration, condition, session_obj)