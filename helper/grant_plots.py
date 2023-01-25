import os
import math
import numpy as np
import pandas as pd
from scipy import signal
from decimal import Decimal
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from collections import defaultdict
from itertools import combinations, permutations
from scipy.stats import ttest_ind, ttest_ind_from_stats, f_oneway
from statsmodels.stats.weightstats import ztest as ztest
import warnings
warnings.filterwarnings("ignore")

# Custom Functions
from plot_helper import smooth_plot, round_up_to_odd, moving_avg, set_plot_params
from two_sample_test import two_sample_test

def significance_test(measure_duration_list, outcome_mag_list, measure):
	"""
	significance_test performs a two sample t-test on the lick/blink data duration list

	Args:
		measure_duration_list (list): list of lick data duration

	Returns:
		t_stat (float): t-statistic
		p_value (float): p-value
	"""
	ANOVA_stat, ANOVA_pvalue = f_oneway(*measure_duration_list)
	ANOVA_p_value_string = '%.2E' % Decimal(ANOVA_pvalue)
	print(' {} ANOVA {} | P-value: {}'.format(outcome_mag_list, round(ANOVA_stat, 3), ANOVA_p_value_string))
	measure_mag_combinations = list(combinations(range(len(outcome_mag_list)), 2))
	measure_duration_combinations = list(combinations(measure_duration_list, 2))
	for m_index, magnitude in enumerate(measure_mag_combinations):
		mag_1 = measure_duration_combinations[m_index][0]
		mag_2 = measure_duration_combinations[m_index][1]
		t, p = ttest_ind(mag_1, 
										 mag_2,
										 equal_var=False)
		p_val_string = '%.2E' % Decimal(p)
		z_val, p_value = ztest(mag_1, mag_2, 
													 alternative='two-sided', 
													 usevar='pooled', 
													 ddof=1.0)
		z_val_string = '%.2E' % Decimal(p_value)
		print('  {}'.format(magnitude), 'T-value: {}'.format(round(t,3)), 'P-value: {} | '.format(p_val_string),
																		'Z-value: {}'.format(round(z_val,3)), 'P-value: {}'.format(z_val_string,3))
		print('    {}'.format(measure_mag_combinations[m_index][0]), 
												'{} Mean: {}'.format(measure, round(np.nanmean(mag_1), 3)),
												'{} Std: {}'.format(measure, round(np.std(mag_1), 3)), 
												'Trials: {}'.format(len(mag_1)))
		print('    {}'.format(measure_mag_combinations[m_index][1]), 
												'{} Mean: {}'.format(measure, round(np.nanmean(mag_2), 3)), 
												'{} Std: {}'.format(measure, round(np.std(mag_2), 3)), 
												'Trials: {}'.format(len(mag_2)))

def grant_plots(session_df, session_obj):

	gs = gridspec.GridSpec(2, 2, width_ratios=[1, 1.5], height_ratios=[1, 1])
	fig_dimensions = [[gs[:, 1], gs[0, 0], gs[1, 0]],
										[gs[:, 0], gs[0, 1], gs[1, 1]]]
	plot_params = ['lick_duration', 'blink_duration_offscreen']
	mag_list = ['reward_mag', 'airpuff_mag']

	COLORS = [['#D2DCD3', '#91BFBC', '#28398D'],
						['#D2DCD3', '#ed8c8c', '#d61313']]

	outcomes = ['Reward', 'Airpuff']
	measures = ['Lick', 'Blink']

	for plot_index, plot_param in enumerate(plot_params):
		outcome = outcomes[plot_index]
		measure = measures[plot_index]
		set_plot_params(FONT=12,
										AXES_TITLE=16,
										AXES_LABEL=18, 
										TICK_LABEL=12, 
										LEGEND=10, 
										TITLE=20)
		params = {"ytick.color" : "w",
          		"xtick.color" : "w",
          		"axes.labelcolor" : "w",
          		"axes.edgecolor" : "w",
							"axes.titlecolor" : "w"}
		# plt.rcParams.update(params)
		fig = plt.figure(figsize=(10, 6))


		FIGURE_SAVE_PATH = session_obj.figure_path
		if 'lick' in plot_param:
			WINDOW_THRESHOLD = session_obj.window_lick
		else:
			WINDOW_THRESHOLD = session_obj.window_blink
		TRIAL_THRESHOLD = 20
		session_df_correct = session_df[session_df['correct'] == 1]
		# only include trials after subject has seen fractal <TRIAL_THRESHOLD> number of times
		session_df_count = session_df_correct[session_df_correct['fractal_count_in_block'] > TRIAL_THRESHOLD]
		# only include one switch (for now)
		session_df_threshold = session_df_count[session_df_count['block'] <= 2]

		# Collapsed on conditions
		ax1 = fig.add_subplot(fig_dimensions[plot_index][0])
		ax1.set_title('Collapsed Across Session', fontsize=18)

		# Condition 1
		ax2 = fig.add_subplot(fig_dimensions[plot_index][1])
		ax2.set_title('Pre-Switch', fontsize=16)

		# Condition 2
		ax3 = fig.add_subplot(fig_dimensions[plot_index][2])
		ax3.set_title('Post-Switch', fontsize=16)
		axarr = [ax1, ax2, ax3]
		TRIAL_THRESHOLD = 10

		outcome_mag_list = sorted(session_df_threshold[mag_list[plot_index]].unique())
		conditions = [[1, 2], [1], [2]]
		# Collapsed on conditions | Condition 1 | Condition 2
		for ax_index, condition in enumerate(conditions):
			measure_duration_list = []
			measure_mean_list = []
			measure_std_list = []
			df_condition = session_df_threshold[session_df_threshold['condition'].isin(condition)]
			# Reward | Airpuff
			for df_index, outcome_mag in enumerate(outcome_mag_list):

				df = df_condition[df_condition[mag_list[plot_index]] == outcome_mag]
				measure_duration = df[plot_param].tolist()
				measure_data_mean = np.nanmean(measure_duration)
				if plot_param == 'lick_duration':
					measure_data_mean = measure_data_mean / 5 # normalize lick data to 1
				measure_duration_list.append(measure_duration)
				measure_std_list.append(np.std(measure_duration))
				measure_mean_list.append(measure_data_mean)
			
			if ax_index == 0: # only print collapsed on conditions
				significance_test(measure_duration_list, outcome_mag_list, measure)

			axarr[ax_index].bar(range(len(measure_mean_list)), 
													measure_mean_list,
													# yerr=measure_std_list,
													color=COLORS[plot_index], linewidth=2)
			axarr[ax_index].set_xticks(range(len(measure_mean_list)))
			outcome_mag_labels = ['none', 'small', 'large']
			axarr[ax_index].set_xticklabels(outcome_mag_labels)
			axarr[ax_index].set_ylim([0,1])
		axarr[0].set_xlabel('{} Magnitude'.format(outcome))
		axarr[0].set_ylabel('Average {} Duration'.format(measure))
		fig.tight_layout()
		# set facecolor to black:
		fig.set_facecolor("k")
		grant_title = 'grant_{}.png'.format(outcomes[plot_index].lower())
		img_save_path = os.path.join(FIGURE_SAVE_PATH, grant_title)
		print('  {} saved.'.format(grant_title))
		plt.savefig(img_save_path, dpi=150, bbox_inches='tight', pad_inches = 0.1)
		plt.close('all')
