import os
from copy import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def outcome_frequency(session_df_correct, session_obj):

	f, axarr = plt.subplots(2, 2, figsize=(7,8))
	FIGURE_SAVE_PATH = session_obj.figure_path
	COLORS = session_obj.colors
	LABELS = copy(session_obj.stim_labels)

	x = []
	y = []
	y2 = []
	num_fractals = len(session_df_correct['stimuli_name'].unique())
	num_conditions = len(session_df_correct['condition'].unique())
	trial_threshold = True if (len(session_df_correct[session_df_correct['condition'] == 1]) > 10) \
												and (len(session_df_correct[session_df_correct['condition'] == 2]) > 10) \
										else False
	for c_index, condition in enumerate(sorted(session_df_correct['condition'].unique())):
		session_df_condition = session_df_correct[session_df_correct['condition'] == condition]
		for f_index, fractal in enumerate(sorted(session_df_condition['stimuli_name'].unique())):
			session_df_fractal_condition = session_df_condition[session_df_condition['stimuli_name'] == fractal]
			# space between conditions
			if (c_index > 0) and (f_index == 0):
				x.append('')
				y.append(0)
				y2.append(0)
			x.append(fractal)
			y.append(np.mean(session_df_fractal_condition['reward']))
			y2.append(np.mean(session_df_fractal_condition['airpuff']))
	x_range = np.arange(len(x))
	bar_colors = COLORS
	bar_labels = LABELS
	if num_conditions > 1 and trial_threshold:
		bar_labels += [''] + LABELS
		bar_colors += ['b'] + COLORS
		axarr[0][0].axvline(num_fractals, color='black')
		axarr[1][0].axvline(num_fractals, color='black')
		axarr[1][0].text((num_fractals*1.5), -0.15, 'Condition 2', ha='center')
	axarr[0][0].bar(x_range, y, color=bar_colors, ec='black')
	axarr[0][0].set_ylabel('Percent of Trials Rewarded')
	axarr[1][0].text((num_fractals/2), -0.15, 'Condition 1', ha='center')
	axarr[1][0].bar(x_range, y2, color=bar_colors, ec='black')
	axarr[1][0].set_ylabel('Percent of Trials Airpuff')
	axarr[0][0].set_xticks(x_range, bar_labels)
	axarr[1][0].set_xticks(x_range, bar_labels)
	# axarr[0][0].text(num_fractals, 1.1, va='center', ha='center', s='Outcome Frequency', fontsize=14, fontweight='bold')
	axarr[0][0].set_title('Outcome Frequency', fontsize=14, fontweight='bold')


	f.tight_layout()
	return f, axarr

def outcome_magnitude(session_df_correct, session_obj, f, axarr):

	FIGURE_SAVE_PATH = session_obj.figure_path
	COLORS = session_obj.colors
	LABELS = copy(session_obj.stim_labels)

	# not all sessions have the new reward/airpuff columns
	if 'reward_drops' not in session_df_correct.columns:
		return

	x = []
	y = []
	y2 = []
	num_fractals = len(session_df_correct['stimuli_name'].unique())
	num_conditions = len(session_df_correct['condition'].unique())
	for c_index, condition in enumerate(sorted(session_df_correct['condition'].unique())):
		session_df_condition = session_df_correct[session_df_correct['condition'] == condition]
		for f_index, fractal in enumerate(sorted(session_df_condition['stimuli_name'].unique())):
			session_df_fractal_condition = session_df_condition[session_df_condition['stimuli_name'] == fractal]
			# space between conditions
			if (c_index > 0) and (f_index == 0):
				x.append('')
				y.append(0)
				y2.append(0)
			x.append(fractal)
			reward_drops = session_df_fractal_condition['reward_drops'].unique()
			y.append(reward_drops[0])
			y2.append(np.mean(session_df_fractal_condition['airpuff_pulses']))
	x_range = np.arange(len(x))
	bar_colors = COLORS
	bar_labels = LABELS
	if num_conditions > 1:
		bar_labels += [''] + LABELS
		bar_colors += ['b'] + COLORS
		axarr[0][1].axvline(num_fractals, color='black')
		axarr[1][1].axvline(num_fractals, color='black')
		axarr[1][1].text((num_fractals*1.5), -0.6, 'Condition 2', ha='center')
	axarr[0][1].bar(x_range, y, color=bar_colors, ec='black')
	axarr[0][1].set_ylabel('Reward Drops')
	axarr[1][1].text((num_fractals/2), -0.6, 'Condition 1', ha='center')
	axarr[1][1].bar(x_range, y2, color=bar_colors, ec='black')
	axarr[1][1].set_ylabel('Airpuff Pulses')
	axarr[0][1].set_xticks(x_range, bar_labels)
	axarr[1][1].set_xticks(x_range, bar_labels)
	axarr[1][1].set_ylim([0, 4.1])
	axarr[0][1].set_title('Outcome Magnitude', fontsize=14, fontweight='bold')
	
	img_save_path = os.path.join(FIGURE_SAVE_PATH, 'outcome_params')
	print('  outcome_params.png saved.')
	f.tight_layout()
	plt.savefig(img_save_path, dpi=150, bbox_inches='tight', pad_inches = 0.1)
	plt.close('all')

def outcome_plots(session_df_correct, session_obj):
	"""
	outcome_plots plots the outcome frequency and magnitude for each fractal

	Args:
		session_df_correct (pd.DataFrame): dataframe of correct trials
		session_obj (Session): session object

	Returns:
		None
	"""
	f, axarr = outcome_frequency(session_df_correct, session_obj)
	outcome_magnitude(session_df_correct, session_obj, f, axarr)
