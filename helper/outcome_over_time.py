import os
import sys
import numpy as np
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt
from collections import defaultdict
# custom functions
from plot_helper import moving_avg

def add_outcome_data(trial, measure_dict, measure):
	valence = trial['valence']
	condition = trial['condition']
	outcome_data = np.nanmean(trial[measure])
	fractal_count = trial['fractal_count_in_block']
	measure_dict[condition][fractal_count].append(outcome_data)
	# print(valence, condition, fractal_count, outcome_data)
	return measure_dict

def outcome_over_time(df, session_obj):
	"""
	Plots the average number of blinks and licks over a session
	"""
	FIGURE_SAVE_PATH = session_obj.figure_path
	avg_window = 10 # N trial rolling avg
	f, axarr = plt.subplots(2, 1, sharey=True, figsize=(10, 7))
	for v_index, valence in enumerate(sorted(df['valence'].unique(), reverse=True)):
		df_valence = df[df['valence'] == valence]
		lick_dict = defaultdict(lambda: defaultdict(list))
		blink_dict = defaultdict(lambda: defaultdict(list))	
		# Add each date to lick/blink dicts
		for date in sorted(df['date'].unique()):
			df_date = df_valence[df_valence['date'] == date]
			for index, trial in df_date.iterrows():
				lick_dict = add_outcome_data(trial, lick_dict, 'lick_count_window')
				blink_dict = add_outcome_data(trial, blink_dict, 'blink_duration_offscreen')
		measure_dicts = [lick_dict, blink_dict]
		for m_index, measure_dict in enumerate(measure_dicts):
			measure_array_1 = moving_avg(list(map(lambda x: np.nanmean(x), measure_dict[1].values())),
																avg_window)
			measure_array_2 = moving_avg(list(map(lambda x: np.nanmean(x), measure_dict[2].values())),
																avg_window)
			measure_array = list(measure_array_1) + list(measure_array_2)
			color=session_obj.valence_colors[valence]
			x_range = np.arange(0, len(measure_array))+avg_window
			axarr[m_index].plot(x_range, measure_array, color=color, label=valence, lw=3)
			axarr[m_index].axhline(y=np.nanmean(measure_array), color=color, linestyle='--', alpha=0.3)
			if v_index == 0:
				axarr[m_index].axvline(x=len(measure_array_1), color='black', alpha=0.3)
	xticklabels = np.arange(avg_window, len(measure_array)+avg_window, avg_window)
	axarr[0].set_ylim([0, 1])
	axarr[0].set_xticks(xticklabels, fontsize=16)
	axarr[0].set_title('Lick Duration', fontsize=20)
	axarr[0].set_xlabel('Trial Number', fontsize=16)
	axarr[0].set_ylabel('Trial Lick (Delay)', fontsize=16)
	axarr[1].set_title('Blink Duration', fontsize=20)
	axarr[1].set_xticks(xticklabels)
	axarr[1].set_xlabel('Trial Number', fontsize=16)
	axarr[1].set_ylabel('Trial Blink (Delay)', fontsize=16)
	f.tight_layout()
	fig_name = 'moving_avg_lick_blink'
	img_save_path = os.path.join(FIGURE_SAVE_PATH, fig_name)
	f.savefig(img_save_path, dpi=150, bbox_inches='tight')
	print('  {}.png saved.'.format(fig_name))
	