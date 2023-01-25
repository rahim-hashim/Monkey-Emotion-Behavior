import os
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
from plot_helper import smooth_plot, round_up_to_odd, moving_avg, set_plot_params
from two_sample_test import two_sample_test

def epoch_time(df):
	# taking the minimum length of epochs to find cutoff values
	# for each epoch of task
	cs_duration_hist = np.array(df['CS Off'].tolist()) - np.array(df['CS On'].tolist())
	cs_end_min = min(cs_duration_hist)
	trace_duration_hist = np.array(df['Trace End'].tolist()) - np.array(df['Trace Start'].tolist())
	trace_end_min = min(trace_duration_hist) + cs_end_min
	outcome_duration_hist = np.array(df['trial_bins'].tolist()) - np.array(df['Trace End'].tolist())
	outcome_end_min = min(outcome_duration_hist) + cs_end_min - 1 # not sure why I included -1 but it was necessary, check this
	return cs_end_min, trace_end_min, outcome_end_min

def raster_binary_valence(session_df, behavioral_code_dict, error_dict, session_obj):

	set_plot_params(FONT=20, AXES_TITLE=22, AXES_LABEL=20, TICK_LABEL=20, LEGEND=16, TITLE=28)

	PRE_CS = 50 # time before CS-on (for moving average calculation)
	FIGURE_SAVE_PATH = session_obj.figure_path
	COLORS = [session_obj.valence_colors[1.0], session_obj.valence_colors[-1.0]]
	WINDOW_THRESHOLD_LICK = session_obj.window_lick
	WINDOW_THRESHOLD_BLINK = session_obj.window_blink

	lick_dict = defaultdict(list)
	blink_dict = defaultdict(list)
	pupil_dict = defaultdict(list)

	lick_epoch_dict = defaultdict(lambda:defaultdict(list))
	blink_epoch_dict = defaultdict(lambda:defaultdict(list))
	pupil_epoch_dict = defaultdict(lambda:defaultdict(list))

	lick_data_probability = defaultdict(list)
	blink_data_probability = defaultdict(list)

	lick_data_duration = defaultdict(list)
	blink_data_duration = defaultdict(list)
	pupil_data_binary = defaultdict(list)

	gs_kw = dict(width_ratios=[5, 1, 1])
	f, axarr = plt.subplots(3,3, gridspec_kw=gs_kw, sharey = False, figsize=(50,20))
	LABELS = session_obj.stim_labels
	num_fractals = len(LABELS)

	TRIAL_THRESHOLD = 10

	# only include trials after subject has seen fractal <TRIAL_THRESHOLD> number of times
	session_df_count = session_df[session_df['fractal_count_in_block'] > TRIAL_THRESHOLD]
	# only include one switch (for now)
	session_df_threshold = session_df_count[session_df_count['block'] <= 2]

	# calculate minimum epoch times
	cs_time_min, trace_time_min, outcome_time_min = epoch_time(session_df_threshold)

	valence_list = sorted(session_df_threshold['valence'].unique(), reverse=True)
	for df_index, valence in enumerate(valence_list):

		if df_index == 0:
			df = session_df_threshold[session_df_threshold['valence'] > 0]
		if df_index == 1:
			df = session_df_threshold[session_df_threshold['valence'] < 0]
		if df_index > 1:
			break

		# valence-specific session lick/blink data
		lick_data_raster = df['lick_raster'].tolist()
		blink_data_raster = df['blink_raster'].tolist()
		pupil_data = df['eye_pupil'].tolist()

		# single bin lick data (-<WINDOW_THRESHOLD>ms from trace interval end)

		for t_index, trial in enumerate(lick_data_raster):

			cs_on_time = df['CS On'].iloc[t_index]
			trace_on_time = df['Trace Start'].iloc[t_index]
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
				pupil_data_trial = range(10000) # for min trial pupil length
			else:
				blink_data_probability[df_index].append(0)
				# only add pupil data if there was no blink
				pupil_data_window = pupil_data[t_index][trace_off_time-WINDOW_THRESHOLD_LICK:trace_off_time]
				pupil_data_window_mean = np.mean(pupil_data_window)
				pupil_data_binary[df_index].append(pupil_data_window_mean)
				pupil_data_trial = pupil_data[t_index][cs_on_time-PRE_CS:]

			# Lick/Blink Duration
			lick_raw = df['lick'].iloc[t_index]
			lick_data_voltage = lick_raw[trace_off_time-WINDOW_THRESHOLD_LICK:trace_off_time]
			lick_data_voltage_mean = np.mean(lick_data_voltage)
			lick_data_duration[df_index].append(lick_data_voltage_mean)

			blink_raw = df['blink_duration_offscreen'].iloc[t_index]
			blink_data_duration[df_index].append(blink_raw)

			lick_data_trial = lick_data_raster[t_index][cs_on_time-PRE_CS:]
			blink_data_trial = blink_data_raster[t_index][cs_on_time-PRE_CS:]

			lick_data_cs = lick_data_raster[t_index][cs_on_time:trace_on_time]
			lick_data_trace = lick_data_raster[t_index][trace_on_time:trace_off_time]
			lick_data_outcome = lick_data_raster[t_index][trace_off_time:]

			blink_data_cs = blink_data_raster[t_index][cs_on_time:trace_on_time]
			blink_data_trace = blink_data_raster[t_index][trace_on_time:trace_off_time]
			blink_data_outcome = blink_data_raster[t_index][trace_off_time:]

			time = np.arange(len(lick_data_trial))

			# lick_data_trial and blink_data_trial are sometimes off by 1 frame
			# 	must investigate further
			shorter_trial_data = min(len(lick_data_trial), len(blink_data_trial), len(pupil_data_trial))
			for bin_num in range(shorter_trial_data):
				lick_dict[bin_num].append(lick_data_trial[bin_num])
				blink_dict[bin_num].append(blink_data_trial[bin_num])
				if 1 not in blink_data_window:
					pupil_dict[bin_num].append(pupil_data_trial[bin_num])

			for bin_num in range(cs_time_min):
				lick_epoch_dict['CS'][bin_num].append(lick_data_cs[bin_num])
				blink_epoch_dict['CS'][bin_num].append(blink_data_cs[bin_num])
			for bin_num in range(trace_time_min-cs_time_min):
				lick_epoch_dict['Trace'][bin_num].append(lick_data_trace[bin_num])
				blink_epoch_dict['Trace'][bin_num].append(blink_data_trace[bin_num])
			for bin_num in range(outcome_time_min-cs_time_min):
				lick_epoch_dict['Outcome'][bin_num].append(lick_data_outcome[bin_num])
				blink_epoch_dict['Outcome'][bin_num].append(blink_data_outcome[bin_num])

		# Now analyze all trials together

		bins = list(lick_dict.keys())
		lick_data_mean = list(map(np.mean, lick_dict.values()))
		blink_data_mean = list(map(np.mean, blink_dict.values()))
		pupil_data_mean = list(map(np.mean, pupil_dict.values()))

		labels = ['rewarded', 'unrewarded']
		label = labels[df_index]

		# Simple Moving Average Smoothing
		WINDOW_SIZE = PRE_CS
		x = np.array(bins[PRE_CS:]) # only capturing post-CS bins
		y1 = moving_avg(lick_data_mean, WINDOW_SIZE)
		axarr[0][0].plot(x, y1[:-1], 
										color=COLORS[df_index], label=label, linewidth=4)
		y2 = moving_avg(blink_data_mean, WINDOW_SIZE)
		axarr[1][0].plot(x, y2[:-1], 
										color=COLORS[df_index], label=label, linewidth=4)
		y3 = moving_avg(pupil_data_mean, WINDOW_SIZE)
		axarr[2][0].plot(range(len(y3)), y3, 
										color=COLORS[df_index], label=label, linewidth=4)

	axarr[0][0].text(0, 1.08, 'CS On', ha='center', va='center', fontsize='large')
	axarr[0][0].text(cs_time_min, 1.08, 'Delay', ha='center', va='center', fontsize='large')
	axarr[0][0].text(trace_time_min, 1.08, 'Outcome', ha='center', va='center', fontsize='large')
	axarr[0][0].set_ylabel('Probability of Lick', fontsize='large')
	axarr[0][0].set_ylim([0, 1.05])
	axarr[0][0].set_yticks(np.arange(0,1.2,0.2).round(1))
	axarr[0][0].set_yticklabels(np.arange(0,1.2,0.2).round(1))
	# lick
	axarr[0][1].set_title('Delay\n(last {}ms)'.format(WINDOW_THRESHOLD_LICK))
	axarr[0][2].set_title('Delay\n(last {}ms)'.format(WINDOW_THRESHOLD_LICK))
	# blink
	axarr[1][1].set_title('Delay\n(last {}ms)'.format(WINDOW_THRESHOLD_BLINK))
	axarr[1][2].set_title('Delay\n(last {}ms)'.format(WINDOW_THRESHOLD_BLINK))
	# pupil
	axarr[2][1].set_title('Delay\n(last {}ms)'.format(WINDOW_THRESHOLD_LICK))
	axarr[2][2].set_title('Delay\n(last {}ms)'.format(WINDOW_THRESHOLD_LICK))

	condition = list(session_df['condition'].unique())[0]
	if condition == 1:
		title = 'Pre-Reversal'
	if condition == 2:
		title = 'Post-Reversal'
	axarr[0][0].set_title(title, pad=25, fontsize=40)
	axarr[0][0].set_xlabel('Time since visual stimuli onset (ms)', fontsize=26)

	axarr[1][0].set_ylabel('Probability of Blink', fontsize=26)
	axarr[1][0].set_ylim([0, 0.8])
	axarr[1][0].set_yticks(np.arange(0,1.0,0.2))
	axarr[1][0].set_xlabel('Time since visual stimuli onset (ms)', fontsize=26)

	axarr[2][0].set_ylabel('Pupil Diameter')
	axarr[2][0].set_xlabel('Time since visual stimuli onset (ms)', fontsize=26)
	
	probability_list = [lick_data_probability, blink_data_probability, pupil_data_binary]
	duration_list = [lick_data_duration, blink_data_duration, pupil_data_binary]
	label_list_prob = ['Lick Probability', 'Blink Probability', 'Avg Pupil Diameter']
	label_list_dur = ['Avg Lick Duration', 'Avg Blink Duration', 'Avg Pupil Diameter']

	for ax_index in range(3):
		# Time Epochs
		axarr[ax_index][0].axvline(0)
		axarr[ax_index][0].axvline(cs_time_min)
		axarr[ax_index][0].axvline(trace_time_min)
		if ax_index == 1:
			window_threshold_label = WINDOW_THRESHOLD_BLINK
		else:
			window_threshold_label = WINDOW_THRESHOLD_LICK
		axarr[ax_index][0].axvspan(xmin=trace_time_min-window_threshold_label,
								xmax=trace_time_min-1,
								ymin=0,
								ymax=1,
								alpha=0.2,
								color='grey')

		axarr[ax_index][0].legend(loc='upper right', frameon=False)
		# Bar Graph - lick/blink probability
		data_probability_mean = list(map(np.mean, probability_list[ax_index].values()))
		print(data_probability_mean)
		axarr[ax_index][1].bar(list(range(2)), data_probability_mean, color=COLORS, ec='black')
		axarr[ax_index][1].set_xticks(list(range(2)))
		axarr[ax_index][1].set_xticklabels(labels, fontsize=26)
		axarr[ax_index][1].set_xlabel('Outcome')
		axarr[ax_index][1].set_ylabel('{}'.format(label_list_prob[ax_index]))
		

		# Bar Graph - lick/blink duration
		data_duration_mean = list(map(np.mean, duration_list[ax_index].values()))
		if ax_index == 0:
			data_duration_mean = list(np.array(data_duration_mean) / 5) # normalize lick data to 0-1
			axarr[ax_index][2].set_ylim([0, 1])
		axarr[ax_index][2].bar(list(range(2)), data_duration_mean, color=COLORS, ec='black')
		axarr[ax_index][2].set_xticks(list(range(2)))
		axarr[ax_index][2].set_xticklabels(labels, fontsize=26)
		axarr[ax_index][2].set_xlabel('Outcome', fontsize=26)
		axarr[ax_index][2].set_ylabel('{}'.format(label_list_dur[ax_index]), fontsize=26)
		if ax_index == 2:
			ymin = min(data_duration_mean) - 100
			ymax = max(data_duration_mean) + 100
			axarr[ax_index][2].set_ylim([ymin, ymax])

	img_save_path = os.path.join(FIGURE_SAVE_PATH, 'raster_by_cond_{}'.format(condition))
	f.tight_layout()
	# f.savefig(img_save_path, dpi=150, bbox_inches='tight', pad_inches = 0.1, transparent=True)
	# print('  raster_by_cond_{}.png saved.'.format(condition))
	plt.show()
	plt.close('all')

