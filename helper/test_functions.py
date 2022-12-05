import os
import sys
import numpy as np
import pandas as pd
# Custom modules
import h5_helper
import preprocess_helper
from Path import Path
from Session import Session
from add_fields import add_fields
pd.options.mode.chained_assignment = None  # default='warn'

ROOT = '/Users/rahimhashim/Google Drive/My Drive/Columbia/Salzman/Monkey-Training/'
# ROOT = '/mnt/g/My Drive/Columbia/Salzman/Monkey-Training/'
EXPERIMENT = 'rhAirpuff'
TASK = 'Probabalistic_Airpuff_4x2'
path_obj = Path(ROOT, EXPERIMENT, TASK)

# Specifying date/monkey/task
start_date = '2022-11-29'
end_date = '2022-11-29'
monkey_input = 'Aragorn'
reprocess_data = True
save_df = True

# parse data
h5_filenames = h5_helper.h5_pull(path_obj.current_dir) # pull all .h5 files from specified directory
ml_config, trial_record, session_df, error_dict, behavioral_code_dict\
	= preprocess_helper.preprocess_data(h5_filenames,
																			path_obj,
																			start_date,
																			end_date,
																			monkey_input,
																			reprocess_data,
																			save_df)

for date in sorted(session_df['date'].unique()):
	print('\nDate: {}'.format(date))

	# from duration_hist import duration_hist
	# duration_hist(session_df_correct, behavioral_code_dict, FIGURE_SAVE_PATH)
	
	session_df_date = session_df[session_df['date'] == date]
	# session_obj contains session metadata
	session_obj = Session(session_df_date, monkey_input, TASK, behavioral_code_dict)

	# adds custom fields
	session_df_date, session_obj = add_fields(session_df_date,
																						session_obj, 
																						behavioral_code_dict)

	from image_diff import image_diff
	FIGURE_SAVE_PATH = image_diff(session_df,
																session_obj,
																path_obj,
																combine_dates=True)

	# from generate_videos import generate_videos
	# session_df_date = generate_videos(session_df_date,
	# 													 	 path_obj, 
	# 													 	 session_obj,
	# 													 	 delay_only=True)

	# Remove failure trials (i.e. break fixation)
	session_df_correct = session_df_date[session_df_date['correct'] == 1]
	session_df_correct = session_df_correct.iloc[:-1]

	from lick_blink_relationship import lick_blink_linear
	lick_blink_linear(session_df_correct, session_obj)

	from session_performance import session_performance
	session_performance(session_df_date, behavioral_code_dict, True, session_obj)

	from session_timing import plot_session_timing
	plot_session_timing(session_df_date, session_obj)

	from outcome_plots import outcome_plots
	outcome_plots(session_df_correct, session_obj)

	# from session_lick import session_lick
	# session_lick(session_df_correct, session_obj)

	from trial_raster import trial_raster
	trial_raster(session_df_correct, session_obj)

	from raster_by_condition import raster_by_condition
	from two_sample_test import t_test_moving_avg
	for condition in sorted(session_df_correct['condition'].unique()):
		session_df_condition = session_df_correct[session_df_correct['condition'] == condition]
		raster_by_condition(session_df_condition, behavioral_code_dict, error_dict, session_obj)
		t_test_moving_avg(session_df_condition, session_obj, condition)
	
	from grant_plots import grant_plots
	grant_plots(session_df_correct, session_obj)

	from markdown_print import markdown_summary
	markdown_summary(session_df_date, behavioral_code_dict, session_obj)

	from measure_hist import measure_hist
	measure_hist(session_df_correct, session_obj)

	from write_to_excel import write_to_excel
	write_to_excel(session_df_date, session_obj, path_obj)

# from regress_behavior import regress_behavior
# regress_behavior(session_df_correct, session_obj)

from trial_movie import select_trial, write_times
write_times(session_obj, session_df)
# select_trial(session_df, session_obj)