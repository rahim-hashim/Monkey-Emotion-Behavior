def run_functions(df, session_obj, path_obj, behavioral_code_dict, error_dict, FIGURE_SAVE_PATH):
	"""
	Runs all analyses functions

	Args:
		df (dataframe): dataframe of session data
		session_obj (Session): session object
		path_obj (Path): path object
		behavioral_code_dict (dict): dictionary of behavioral codes
		error_dict (dict): dictionary of error codes
		FIGURE_SAVE_PATH (str): path to save figures

	Returns:
		session_obj (Session): updated session object
	"""

	session_obj.save_paths(path_obj.TARGET_PATH, 
												 path_obj.TRACKER_PATH, 
												 path_obj.VIDEO_PATH,
												 FIGURE_SAVE_PATH)

	from lick_blink_relationship import lick_blink_linear
	lick_blink_linear(df, session_obj)

	from session_performance import session_performance
	session_performance(df, behavioral_code_dict, True, session_obj)

	from session_timing import plot_session_timing
	plot_session_timing(df, session_obj)

	from outcome_plots import outcome_plots
	outcome_plots(df, session_obj)

	from session_lick import session_lick
	session_lick(df, session_obj)

	from trial_raster import trial_raster
	trial_raster(df, session_obj)

	from raster_by_condition import raster_by_condition
	from two_sample_test import t_test_moving_avg
	for block in sorted(df['block'].unique()):
		session_df_condition = df[df['block'] == block]
		raster_by_condition(session_df_condition, session_obj)
		t_test_moving_avg(session_df_condition, session_obj, block)
	
	from grant_plots import grant_plots
	grant_plots(df, session_obj)

	from measure_hist import measure_hist
	measure_hist(df, session_obj)

	from eyetracking_analysis import eyetracking_analysis
	eyetracking_analysis(df, session_obj, TRIAL_THRESHOLD=10)

	from outcome_over_time import outcome_over_time
	outcome_over_time(df, session_obj)

	from markdown_print import markdown_summary
	markdown_summary(df, behavioral_code_dict, session_obj)

	from write_to_excel import write_to_excel
	write_to_excel(df, session_obj, path_obj)

	return session_obj