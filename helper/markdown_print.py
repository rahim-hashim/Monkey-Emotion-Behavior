import os
import re
import math
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from operator import itemgetter
from IPython.display import Markdown, display
from collections import defaultdict, OrderedDict

weekday_dict = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thurs', 4:'Fri', 5:'Sat', 6:'Sun'} # for date printing

def printmd(string):
	display(Markdown(string))

def configure_plotly_browser_state():
	"""
	configure_plotly_browser_state is called to print 
	Markdown text to the console
	"""
	import IPython
	display(IPython.core.display.HTML('''
		<script src="/static/components/requirejs/require.js"></script>
		<script>
			requirejs.config({
				paths: {
					base: '/static/base',
					plotly: 'https://cdn.plot.ly/plotly-latest.min.js?noext',
				},
			});
		</script>
		'''))

def markdown_calc(df, f, behavioral_code_dict, session_obj, verbose):

	md_list = [] # list of all markdown text to be printed

	# Date
	date = df['date'].iloc[0]
	date_formatted = '20' + date
	datem = datetime.strptime(date, '%y%m%d')
	weekday = datem.weekday()
	weekday_str = weekday_dict[weekday]
	d = datem.strftime('%B %d, %Y')
	date_str = '# {}, {}\n'.format(weekday_str, d)
	md_list.append(date_str)
	f.write(date_str)
	
	# Task
	task = session_obj.task
	task_str = '\n## {}\n'.format(task)
	md_list.append(task_str)
	f.write(task_str)

	# Attempts
	attempts_header = '\n### Attempts\n'
	md_list.append(attempts_header)
	f.write(attempts_header)

	# Session Time
	session_datetime = df['trial_datetime_start'].iloc[0]
	session_datetime_formatted = session_datetime.strftime('%I:%M %p')
	session_datetime_str = '* **Start Time:** ' + str(session_datetime_formatted) + '\n'
	md_list.append(session_datetime_str)
	f.write(session_datetime_str)

	# Session Length
	session_time = session_obj.session_time
	session_time_min = session_time*60
	session_time_str = '* **Total Time:** ' + str(session_time) + ' hrs\n'
	md_list.append(session_time_str)
	f.write(session_time_str)

	# Number of Trials
	num_trials = len(df)
	num_correct_trials = df['correct'].sum()
	total_trials_str = '* **Total Trials:** ' + str(num_trials) + '\n'
	md_list.append(total_trials_str)
	f.write(total_trials_str)

	# Attempts per Min
	total_attempts_min = session_obj.total_attempts_min
	total_attempts_min_str = '* **Attempts per min:** ' + str(total_attempts_min) + '\n'
	md_list.append(total_attempts_min_str)
	f.write(total_attempts_min_str)

	# Number of Trials (Initiated)
	total_initiated_perc = session_obj.prop_trials_initiated * 100
	total_initiated_str = '* **Initiated Trials:** ' + str(total_initiated_perc) +'%' +\
										' ({}/{})'.format(num_correct_trials, len(df)) + '\n'
	md_list.append(total_initiated_str)
	f.write(total_initiated_str)

	# CS On Performance
	CS_on_trials = session_obj.CS_on_trials
	perf_CS_on_round = session_obj.prop_correct_CS_on * 100
	perf_CS_on_str = '* **CS On:** ' + str(perf_CS_on_round) + '%' +\
							' ({}/{})'.format(num_correct_trials, CS_on_trials) +  '\n'
	md_list.append(perf_CS_on_str)
	f.write(perf_CS_on_str)

	# Outcome Summary
	outcome_summary_str = '* **Outcome Summary**\n'
	md_list.append(outcome_summary_str)
	f.write(outcome_summary_str)
	avg_lick = session_obj.lick_duration['all']
	avg_lick_str = '\t* *Mean Lick Duration:* ' + str(avg_lick)+  '\n'
	md_list.append(avg_lick_str)
	f.write(avg_lick_str)
	avg_blink = session_obj.blink_duration['all']
	avg_blink_str = '\t* *Mean Blink Duration:* ' + str(avg_blink)+  '\n'
	md_list.append(avg_blink_str)
	f.write(avg_blink_str)

	# Fractals
	fractal_img_path = os.path.join('..', 'figures', date_formatted, '_fractals.png') 
	fractal_form_str = '<img src="{}">'.format(fractal_img_path)
	fractal_str = '\n### Fractals\n{}\n'.format(fractal_form_str)
	md_list.append(fractal_str)
	f.write(fractal_str)

	# Outcome Parameters
	outcome_param_header = '\n### Outcome Parameters\n'
	md_list.append(outcome_param_header)
	f.write(outcome_param_header)

	outcome_param_img_path = os.path.join('..', 'figures', date_formatted, 'outcome_params.png') 
	outcome_param_img_path_str = '<img src="{}" style="zoom:50%;">\n'.format(outcome_param_img_path)
	md_list.append(outcome_param_img_path_str)
	f.write(outcome_param_img_path_str)

	# Performance
	performance_header = '\n### Performance\n'
	md_list.append(performance_header)
	f.write(performance_header)

	perf_img_path = os.path.join('..', 'figures', date_formatted, 'perf_by_fractal.png') 
	perf_form_str = '<img src="{}">\n\n'.format(perf_img_path)
	md_list.append(perf_form_str)
	f.write(perf_form_str)

	# Latency
	latency_header = '\n### Latency\n'
	md_list.append(latency_header)
	f.write(latency_header)
	latency_session_img_path = os.path.join('..', 'figures', date_formatted, 'session_latency.png')
	latency_session_img_path_str = '<img src="{}">\n'.format(latency_session_img_path)
	md_list.append(latency_session_img_path_str)
	f.write(latency_session_img_path_str)

	# Session Data
	session_str = '\n### Session Data\n'
	md_list.append(session_str)
	f.write(session_str)

	# Session Lick/Blink Duration
	session_lick_blink_header = '#### Lick/Blink Duration\n'
	md_list.append(session_lick_blink_header)
	f.write(session_lick_blink_header)

	session_lick_blink_img_path = os.path.join('..', 'figures', date_formatted, 'moving_avg_lick_blink.png')
	session_lick_blink_img_path_str = '<img src="{}">\n'.format(session_lick_blink_img_path)
	md_list.append(session_lick_blink_img_path_str)
	f.write(session_lick_blink_img_path_str)

	# Session Average Lick Probability
	lick_header = '#### Avg Lick Probability\n'
	md_list.append(lick_header)
	f.write(lick_header)

	lick_session_img_path = os.path.join('..', 'figures', date_formatted, 'session_lick_avg.png')
	lick_session_img_str = '<img src="{}">\n'.format(lick_session_img_path)
	md_list.append(lick_session_img_str)
	f.write(lick_session_img_str)

	# Session Average Blink Probability
	blink_header = '#### Avg Blink Probability\n'
	md_list.append(blink_header)
	f.write(blink_header)

	blink_session_img_path = os.path.join('..', 'figures', date_formatted, 'session_blink_avg.png')
	blink_session_img_str = '<img src="{}">\n'.format(blink_session_img_path)
	md_list.append(blink_session_img_str)
	f.write(blink_session_img_str)

	# Raster by Trial
	raster_fractal_header = '\n### Raster by Trial\n'
	md_list.append(raster_fractal_header)
	f.write(raster_fractal_header)

	# Raster by Fractal
	## Lick
	lick_img_path = os.path.join('..', 'figures', date_formatted, 'fractal_lick_raster.png')
	lick_form_str = '<img src="{}" style="zoom:75%;">\n'.format(lick_img_path)
	md_list.append(lick_form_str)
	f.write(lick_form_str)
	## Blink
	blink_img_path = os.path.join('..', 'figures', date_formatted, 'fractal_blink_raster.png')
	blink_form_str = '<img src="{}" style="zoom:75%;">\n'.format(blink_img_path)
	md_list.append(blink_form_str)
	f.write(blink_form_str)

	trial_avg_header = '\n### Trial Average Data\n'
	md_list.append(trial_avg_header)
	f.write(trial_avg_header)

	# Raster by Condition
	conditions = sorted(list(df['condition'].unique()))
	for condition in conditions:
		condition_str = '#### Condition {}\n'.format(condition)
		md_list.append(condition_str)
		f.write(condition_str)
		lick_img_path = os.path.join('..', 'figures', date_formatted, 'raster_by_cond_{}.png'.format(condition)) 
		lick_form_str = '<img src="{}">\n'.format(lick_img_path)
		md_list.append(lick_form_str)
		f.write(lick_form_str)

	# T-Test (Lick/Blink)
	t_test_header = '\n### T-Test\n'
	md_list.append(t_test_header)
	f.write(t_test_header)
	for condition in conditions:
		condition_str = '#### Condition {}\n'.format(condition)
		md_list.append(condition_str)
		f.write(condition_str)
		## Lick
		t_test_lick_img_path = os.path.join('..', 'figures', date_formatted, 't_test_lick-duration_{}.png'.format(condition))
		t_test_lick_img_path_str = '<img src="{}">\n'.format(t_test_lick_img_path)
		md_list.append(t_test_lick_img_path_str)
		f.write(t_test_lick_img_path_str)
		## Blink Duration
		t_test_blink_img_path = os.path.join('..', 'figures', date_formatted, 't_test_blink-duration_{}.png'.format(condition))
		t_test_blink_img_path_str = '<img src="{}">\n'.format(t_test_blink_img_path)
		md_list.append(t_test_blink_img_path_str)
		f.write(t_test_blink_img_path_str)
		## Blink Probability
		t_test_blink_img_path = os.path.join('..', 'figures', date_formatted, 't_test_blink-prob_{}.png'.format(condition))
		t_test_blink_img_path_str = '<img src="{}">\n'.format(t_test_blink_img_path)
		md_list.append(t_test_blink_img_path_str)
		f.write(t_test_blink_img_path_str)

	# Mean Lick/Blink Duration by Condition
	collapsed_outcome_header = '\n### Collapse Across Conditions\n'
	md_list.append(collapsed_outcome_header)
	f.write(collapsed_outcome_header)
	outcome_path = os.path.join('..', 'figures', date_formatted, 'grant_reward.png')
	outcome_fig_str = '<img src="{}">\n'.format(outcome_path)
	md_list.append(outcome_fig_str)
	f.write(outcome_fig_str)
	outcome_path = os.path.join('..', 'figures', date_formatted, 'grant_airpuff.png')
	outcome_fig_str = '<img src="{}">\n'.format(outcome_path)
	md_list.append(outcome_fig_str)
	f.write(outcome_fig_str)

	# Distribution of Lick/Blink Duration
	dist_path = os.path.join('..', 'figures', date_formatted, 'lick_blink_hist.png')
	dist_fig_str = '<img src="{}">\n'.format(dist_path)
	md_list.append(dist_fig_str)
	f.write(dist_fig_str)

	cdf_dist_path = os.path.join('..', 'figures', date_formatted, 'lick_blink_cdf.png')
	cdf_fig_str = '<img src="{}">\n'.format(cdf_dist_path)
	md_list.append(cdf_fig_str)
	f.write(cdf_fig_str)

	# Session Average Lick Probability
	lick_blink_header = '### Lick Blink Relationship\n'
	md_list.append(lick_blink_header)
	f.write(lick_blink_header)
	lick_blink_path = os.path.join('..', 'figures', date_formatted, 'lick_vs_blink.png')
	lick_blink_fig_str = '<img src="{}">\n'.format(lick_blink_path)
	md_list.append(lick_blink_fig_str)
	f.write(lick_blink_fig_str)

	line_break = '\n***\n'
	f.write(line_break)

	# Eye Position Analysis
	eye_heatmap_header = '### Eye Position Heatmap\n'
	md_list.append(eye_heatmap_header)
	f.write(eye_heatmap_header)
	for valence in sorted(df['valence'].unique(), reverse=True):
		eye_heatmap_path = os.path.join('..', 'figures', date_formatted, 'eye_heatmap_{}.png'.format(valence))
		eye_heatmap_fig_str = '<img src="{}">\n'.format(eye_heatmap_path)
		md_list.append(eye_heatmap_fig_str)
		f.write(eye_heatmap_fig_str)
	line_break = '\n***\n'
	f.write(line_break)

	if verbose:
		for md_string in md_list:
			printmd(md_string)

	return f

def markdown_summary(df, behavioral_code_dict, session_obj):

	TRACKER_PATH = session_obj.tracker_path

	MARKDOWN_PATH = os.path.join(TRACKER_PATH, 'markdowns')
	if os.path.exists(MARKDOWN_PATH) == False:
		os.mkdir(MARKDOWN_PATH)

	print('\nGenerating session summary: {}'.format(MARKDOWN_PATH))
	# Calculate performance of each date individually
	for date in df['date'].unique():
		date_formatted = '20' + date
		print('  Writing {}.md'.format(date_formatted))
		file_path = os.path.join(MARKDOWN_PATH, date_formatted+'.md')
		with open(file_path, 'w') as f:
			df_date = df[df['date'] == date]
			f = markdown_calc(df_date, f, behavioral_code_dict, session_obj, verbose=False)

	f.close()

	# # Calculate performance for all dates combined
	# if len(df['date'].unique()) > 1:
	# 	all_str = '## All Dates\n'
	# 	md_list.append(all_str)
	# 	f.write(all_str)	
	# 	figure_path_date = None

	# 	markdown_calc(df, f, behavioral_code_dict)