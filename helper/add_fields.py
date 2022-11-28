import math
import numpy as np
import pandas as pd
from textwrap import indent
from pprint import pprint, pformat
from collections import defaultdict, OrderedDict

def add_epoch_times(df, behavioral_code_dict):
	"""
	Adds columns for each epoch time start to session_df

	Args:
		df: session DataFrame
		behavioral_code_dict: dictionary of all MonkeyLogic code mappings
			
	Returns:
		df: session DataFrame now including marker time for each behavioral code
	"""

	behavioral_code_indices = list(behavioral_code_dict.keys())
	behavioral_code_names = list(behavioral_code_dict.values())

	epoch_dict = defaultdict(list)
	for t_index in range(len(df)):
		markers = df['behavioral_code_markers'].iloc[t_index]
		times = df['behavioral_code_times'].iloc[t_index]

		for k_index, key in enumerate(behavioral_code_indices):
			epoch_name = behavioral_code_names[k_index]
			try:
				epoch_marker = markers.index(key)
				epoch_dict[epoch_name].append(int(times[epoch_marker]))
			except:
				epoch_dict[epoch_name].append(np.nan)

	for k_index, key in enumerate(epoch_dict.keys()):
		if key != 'Not assigned':
			df[key] = list(epoch_dict.values())[k_index]
			df[key] = df[key].astype('Int32')
	return df

def valence_assignment(row):
	"""
	Adds column for valence of stimuli which includes
	the intensity of the stimuli

	Args:
		row: session DataFrame row
			
	Returns:
		valence: scalar value of valence of stimuli [1, 0.5, -0.5, -1]
	"""
	valence = 0
	# airpuff 
	if row['reward_mag'] == 0:
		if row['airpuff_mag'] == 1:
			valence = -1
		else:
			valence = -0.5
	# reward
	else:
		if row['reward_mag'] == 1:
			valence = 1
		else:
			valence = 0.5
	return valence

def trace_to_raster(trace_data, threshold):
	"""
	trace_to_raster converts the lick data to a binary
	probability of licking

	Args:
		trace_data: raw lick trace data from MonkeyLogic
		threshold: manual threshold placed to count a lick (default: 1)
			
	Returns:
		raster_data: rasterized data for each ms window
	"""

	raster_data = []
	for l_index, trace_bin in enumerate(trace_data):
		if trace_bin >= threshold or trace_bin <= (-1*threshold):
			#raster_dict[l_index].append(1)
			raster_data.append(1)
		else:
			#raster_dict[l_index].append(0)
			raster_data.append(0)
	return raster_data

def lick_window(trial):
	"""
	Generates an array for each trial of rasterized lick data
			
		Args:
			trial: row in session_df DataFrame
			
		Returns:
			lick_raster: rasterized lick data for each ms window
	"""
	
	LICK_THRESHOLD = 4
	lick_data = trial['lick'].tolist()
	lick_raster = trace_to_raster(lick_data, LICK_THRESHOLD)
	#lick_window_list = lick_dict.values()
	#lick_window_list_flat = [item for sublist in lick_window_list for item in sublist]
	#lick_mean = np.mean(lick_window_list_flat)
	return lick_raster

def blink_window(trial):
	"""
	Generates an array for each trial of rasterized blink data
			
		Args:
			trial: row in session_df DataFrame
			
		Returns:
			blink_raster: rasterized blink data for each ms window
	"""

	# EyeLink (x,y) values for eyes offscreen
	BLINK_SIGNAL = 10

	eye_x = trial['eye_x'].tolist()
	eye_y = trial['eye_y'].tolist()

	eye_x_abs = [abs(x) for x in eye_x]
	eye_y_abs = [abs(y) for y in eye_y]

	eye_zipped = list(map(max, zip(eye_x_abs, eye_y_abs)))
	blink_raster = trace_to_raster(eye_zipped, BLINK_SIGNAL)

	return blink_raster

def trial_bins(trial):
	"""
	Uses the number of samples of eye data as a proxy for
	the trial bins
			
		Args:
			trial: row in session_df DataFrame
			
		Returns:
			trial_length: number of samples of eye_x data
	"""

	trial_length = len(trial['eye_x'].tolist())
	return trial_length

def trial_in_block(df):
	"""
	Counts the trial number in a block

		Args:
			df: session_df DataFrame
			
		Returns:
			trial_block_count: list of trial block count
	"""
	count = 0
	trial_block_count = []
	for t_index in range(len(df)): # off by 1 because len = max(t_index) + 1
		if t_index == 0:
			pass 											 # skipping the first index corrects the offset
		else:
			if df['block'].iloc[t_index] != df['block'].iloc[t_index-1]:
				count = 0
		trial_block_count.append(count)
		count += 1
	return trial_block_count

def fractal_in_block(df):
	"""
	Counts the number of times the fractal was presented in a block

		Args:
			df: session_df DataFrame
			
		Returns:
			fractal_count: trial presentation number in block
	"""

	fractals = sorted(df['stimuli_name'].unique())
	zero_counter = np.zeros(len(fractals), dtype=int)
	fractal_count = []
	for trial in range(len(df)):
		if df['trial_in_block'].iloc[trial] == 0:
			zero_counter = np.zeros(len(fractals), dtype=int)
		fractal = df['stimuli_name'].iloc[trial]
		fractal_index = fractals.index(fractal)
		zero_counter[fractal_index] += 1
		fractal_count.append(zero_counter[fractal_index])
	return fractal_count

def outcome_back_counter(df):
	df['reward_1_back'] = df.reward.shift(1)
	df['reward_2_back'] = df['reward_1_back'].tolist() + df.reward.shift(2)	
	df['reward_3_back'] = df['reward_2_back'].tolist() + df.reward.shift(3)
	df['reward_4_back'] = df['reward_3_back'].tolist() + df.reward.shift(4)
	df['reward_5_back'] = df['reward_4_back'].tolist() + df.reward.shift(5)
	df['airpuff_1_back'] = df.airpuff.shift(1)
	df['airpuff_2_back'] = df['airpuff_1_back'].tolist() + df.airpuff.shift(2)	
	df['airpuff_3_back'] = df['airpuff_2_back'].tolist() + df.airpuff.shift(3)
	df['airpuff_4_back'] = df['airpuff_3_back'].tolist() + df.airpuff.shift(4)
	df['airpuff_5_back'] = df['airpuff_4_back'].tolist() + df.airpuff.shift(5)
	return df

def lick_count_window(trial, trace_window):
	"""
	Generates an array for each trial of rasterized lick data
			
		Args:
			trial: row in session_df DataFrame
			
		Returns:
			lick_data_window: rasterized lick data for <session_df.window> ms window before
				'Trace End' i.e. Delay timepoint
	"""
	lick_raster = trial['lick_raster']
	trace_off_time = trial['Trace End']
	try:
		lick_data_window = lick_raster[trace_off_time-trace_window:trace_off_time]
	except: # error before 'Trace End'
		lick_data_window = np.nan
	return lick_data_window

def blink_count_window(trial, trace_window):
	"""
	Generates an array for each trial of rasterized blink data
			
		Args:
			trial: row in session_df DataFrame
			
		Returns:
			blink_data_window: rasterized blink data for <session_obj.window>ms window before
				'Trace End' i.e. Delay timepoint
	"""
	eye_raster = trial['blink_raster']
	trace_off_time = trial['Trace End']
	try:
		blink_data_window = eye_raster[trace_off_time-trace_window:trace_off_time]
	except: # error before 'Trace End'
		blink_data_window = np.nan		
	return blink_data_window
	
def pupil_window(trial):
	"""
	Generates an array for each trial of pupil data
			
		Args:
			trial: row in session_df DataFrame
			
		Returns:
			pupil_data_window: pupil data for <session_obj.window>ms window before
	"""
	pupil_data = trial['eye_pupil']
	cs_off_time = trial['CS Off']
	trace_off_time = trial['Trace End']
	try:
		pupil_data_window = pupil_data[cs_off_time:trace_off_time]
	except: # error before 'Trace End'
		pupil_data_window = np.nan		
	return pupil_data_window

def pupil_pre_CS(trial):
	"""
	Generates an array for each trial of pupil data
			
		Args:
			trial: row in session_df DataFrame
			
		Returns:
			pupil_data_window: pupil data for 200ms before CS On
	"""
	pupil_data = trial['eye_pupil']
	cs_on_time = trial['CS On']
	try:
		pupil_data_window = pupil_data[cs_on_time-200:cs_on_time]
	except: # error before 'CS On'
		pupil_data_window = np.nan	
	return pupil_data_window

def lick_in_window(trial):
	lick_count_window = trial['lick_count_window']
	if type(lick_count_window) == float: # np.nan
		return np.nan
	elif 1 in lick_count_window:
		return 1
	else:
		return 0

def blink_in_window(trial):
	blink_count_window = trial['blink_count_window']
	if type(blink_count_window) == float: # np.nan
		return np.nan
	elif 1 in blink_count_window:
		return 1
	else:
		return 0

def lick_duration(trial, trace_window):

	lick_vals = trial['lick']
	trace_off_time = trial['Trace End']
	try:
		lick_window = lick_vals[trace_off_time-trace_window:trace_off_time]
		lick_avg = np.nanmean(lick_window)
	except:
		lick_avg = np.nan
	return lick_avg  

def blink_duration_sig(trial, trace_window, blink_signal):

	eye_x, eye_y = trial['eye_x'], trial['eye_y']
	trace_off_time = trial['Trace End']
	try:
		eye_x_window = eye_x[trace_off_time-trace_window:trace_off_time]
		eye_y_window = eye_y[trace_off_time-trace_window:trace_off_time]
		blink_count = [1 if (x,y) in blink_signal else 0 for (x,y) in zip(eye_x_window, eye_y_window)]
		blink_avg = np.nanmean(blink_count)
	except:
		blink_avg = np.nan
	return blink_avg  

def blink_duration_offscreen(trial, trace_window):

	blink_count_window = trial['blink_count_window']
	if type(blink_count_window) == float: # np.nan
		blink_avg = np.nan
	else:
		blink_avg = np.nanmean(blink_count_window)
	return blink_avg

def eye_distance(trial, session_obj):
	"""
	Calculates the total distance that the animal's eyes traveled 
	during the trial

	Args:
		trial: row in session_df DataFrame
		session_obj: session object

	Returns:
		eye_distance: total distance that the animal's eyes traveled
			during the trial
	"""
	trace_window = session_obj.window_blink
	blink_signal = session_obj.blink_signal
	trace_off_time = trial['Trace End']
	try:
		eye_x_window = list(trial['eye_x'][trace_off_time-trace_window:trace_off_time])
		eye_y_window = list(trial['eye_y'][trace_off_time-trace_window:trace_off_time])
		blink_signal_list = []
		for bin, (x,y) in enumerate(zip(eye_x_window, eye_y_window)):
			if x in blink_signal.values() and y in blink_signal.values():
				blink_signal_list.append(bin)
		# remove offscreen eye data (variable signal each day)
		for index in sorted(blink_signal_list, reverse=True):
				del eye_x_window[index]
				del eye_y_window[index]
		dx = np.diff(eye_x_window)
		dy = np.diff(eye_y_window)
		step_size = np.sqrt(dx**2+dy**2)
		cumulative_distance = np.sum(step_size)
	except:
		cumulative_distance = np.nan # trial error before 'Trace End'
	return cumulative_distance

def prelim_behavior_analysis(df, session_obj, behavioral_code_dict):
	# total lick rate
	lick_dur_all = round(np.mean(df[df['correct']==1]['lick_duration'].tolist())/5, 3)
	session_obj.lick_duration['all'] = lick_dur_all
	# total blink rate
	avg_blink_all = round(np.mean(df[df['correct']==1]['blink_duration_offscreen'].tolist()), 3)
	session_obj.blink_duration['all'] = avg_blink_all
	return session_obj

def parse_valence_labels(df, session_obj):
	"""
	Parses valence labels

	Args:
		df: session_df DataFrame
		session_obj: session object

	Returns:
		session_obj: session object with updated valence labels
	"""
	valence_labels = sorted(df['valence'].unique(), reverse=True)
	for valence in valence_labels:
		if valence == -1:
			session_obj.valence_labels[valence] = '(-)(-)'
		elif valence == -0.5:
			session_obj.valence_labels[valence] = '(-)'
		elif valence == 0:
			session_obj.valence_labels[valence] = '(0)'
		elif valence == 0.5:
			session_obj.valence_labels[valence] = '(+)'
		elif valence == 1:
			session_obj.valence_labels[valence] = '(+)(+)'
	return session_obj

def add_fields(df, session_obj, behavioral_code_dict):
	print(' Adding additional fields to session_df DataFrame...')

	TRACE_WINDOW_LICK = session_obj.window_lick
	TRACE_WINDOW_BLINK = session_obj.window_blink
	eye_blink_signal = session_obj.blink_signal
	BLINK_SIGNAL = [(eye_blink_signal['eye_x_min'], eye_blink_signal['eye_y_min']),
									(eye_blink_signal['eye_x_max'], eye_blink_signal['eye_y_max'])]

	df = add_epoch_times(df, behavioral_code_dict)
	df['valence'] = df.apply(valence_assignment, axis=1)
	df['lick_raster'] = df.apply(lick_window, axis=1)
	df['blink_raster'] = df.apply(blink_window, axis=1)
	df['trial_bins'] = df.apply(trial_bins, axis=1)
	df['trial_in_block'] = trial_in_block(df)
	df['fractal_count_in_block'] = fractal_in_block(df)
	df = outcome_back_counter(df)
	df['lick_count_window'] = df.apply(lick_count_window, trace_window=TRACE_WINDOW_LICK, axis=1)
	df['blink_count_window'] = df.apply(blink_count_window, trace_window=TRACE_WINDOW_BLINK, axis=1)
	df['pupil_window'] = df.apply(pupil_window, axis=1)
	df['pupil_pre_CS'] = df.apply(pupil_pre_CS, axis=1)
	df['lick_in_window'] = df.apply(lick_in_window, axis=1)
	df['blink_in_window'] = df.apply(blink_in_window, axis=1)
	df['lick_duration'] = df.apply(lick_duration, 
																	trace_window=TRACE_WINDOW_LICK, 
																	axis=1)	
	df['blink_duration_sig'] = df.apply(blink_duration_sig, 
																	trace_window=TRACE_WINDOW_BLINK,
																	blink_signal=BLINK_SIGNAL, 
																	axis=1)
	df['blink_duration_offscreen'] = df.apply(blink_duration_offscreen, 
																	trace_window=TRACE_WINDOW_BLINK, 
																	axis=1)
	df['eye_distance'] = df.apply(eye_distance, 
																session_obj=session_obj, 
																axis=1)
	print('  {} new fields added.'.format(20))

	session_obj = prelim_behavior_analysis(df, session_obj, behavioral_code_dict)
	session_obj = parse_valence_labels(df, session_obj)
	print(indent(pformat(df.columns), '  '))

	return df, session_obj
