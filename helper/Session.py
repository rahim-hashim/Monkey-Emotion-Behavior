import os
import numpy as np
import pandas as pd
import matplotlib as mpl
from collections import defaultdict
from datetime import datetime, timedelta

#COLORS = ['#905C99', '#907F9F', '#B0C7BD', '#B8EBD0']

def colorFader(c1,c2,mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
	c1=np.array(mpl.colors.to_rgb(c1))
	c2=np.array(mpl.colors.to_rgb(c2))
	return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

class Session:
	def __init__(self, df, monkey_input, task, behavioral_code_dict):
		print(' Creating Session Objects...')
		self.df = df
		self.monkey = monkey_input
		self.task = task
		self.window_lick = 750
		self.window_blink = 1000
		self.colors = []
		self.stim_labels = []
		self.valence_colors = ['#28398D', '#91BFBC', '#ED8C8C', '#D61313'] # dark blue, blue, red, dark red
		self.valence_labels = defaultdict(str)
		self.session_num = 0						# can be multiple sessions per monkey per day
		self.session_length = 0					# length of each session in seconds
		self.session_time = 0						# length of each session in hours
		self.total_attempts_min = 0 		# total attempts per min per session
		self.prop_trials_initiated = 0	# fraction of initiated trials per session
		self.CS_on_trials = 0						# number of "CS On" trials per session
		self.prop_correct_CS_on = 0			# fraction of correct initiated trials per session
		self.reward_outcome_params = defaultdict(list)
		self.airpuff_outcome_params = defaultdict(list)
		self.lick_duration = defaultdict(float)
		self.blink_duration = defaultdict(float)
		self.blink_signal = defaultdict(float)
		self.task_path = ''
		self.figure_path = ''
		self.tracker_path = ''
		self.video_path = ''
		self.parse_stim_labels()
		self.generate_colors()
		self.calculate_datetime()
		self.find_offscreen_values()
		self.find_outcome_parameters()
		self.behavior_summary(behavioral_code_dict)
	
	def parse_stim_labels(self):
		unique_fractals = self.df['stimuli_name'].unique()
		self.stim_labels = sorted([fractal.split('_')[-1] for fractal in unique_fractals])

	def generate_colors(self):
		n = len(self.stim_labels)
		c1 = '#452c49' # dark magenta
		c2 = '#99ffff' # light cyan
		n = len(self.stim_labels)
		for x in range(n):
			color=colorFader(c1,c2,x/n)
			self.colors.append(color)

	def calculate_datetime(self):
		session = self.df
		self.session_num = session['session_num'].iloc[0]
		session_length = session['trial_start'].iloc[-1]
		session_start = session['trial_datetime_start'].iloc[0]
		session_end = session['trial_datetime_end'].iloc[-1]
		session_time = session_end - session_start
		session_length_timedelta = timedelta(seconds=session_time.seconds)
		self.session_length = session_length_timedelta
		session_time = round(session_length/(1000*60*60), ndigits=2)
		self.session_time = session_time

	def save_paths(self, TASK_PATH, TRACKER_PATH, VIDEO_PATH, FIGURE_PATH):
		self.task_path = TASK_PATH
		self.tracker_path = TRACKER_PATH
		self.video_path = VIDEO_PATH
		self.figure_path = FIGURE_PATH

	def find_offscreen_values(self):
		"""
		Finds the x and y coordinates of the offscreen EyeSignal value
		which is different each time you calibrate (i.e. each session)
		"""
		df = self.df
		eye_x_min = 0; eye_y_min = 0
		eye_x_max = 0; eye_y_max = 0
		for trial_num in range(5):
			eye_x = df['eye_x'].iloc[trial_num]
			eye_y = df['eye_y'].iloc[trial_num]
			if min(eye_x) < eye_x_min:
				eye_x_min = min(eye_x)			
			if min(eye_y) < eye_y_min:	
				eye_y_min = min(eye_y)
			if max(eye_x) > eye_x_max:
				eye_x_max = max(eye_x)
			if max(eye_y) > eye_y_max:	
				eye_y_max = max(eye_y)
		print('  Max Values (X,Y): ({},{})'.format(round(eye_x_min,3),
																							 round(eye_y_min,3)))
		print('  Max Values (X,Y): ({},{})'.format(round(eye_x_max,3),
																							 round(eye_y_max,3)))
		self.blink_signal['eye_x_min'] = eye_x_min
		self.blink_signal['eye_y_min'] = eye_y_min
		self.blink_signal['eye_x_max'] = eye_x_max
		self.blink_signal['eye_y_max'] = eye_y_max

	def find_outcome_parameters(self):
		df = self.df.copy()
		df = df[df['correct'] == 1]
		reward_mag_list = []
		reward_freq_list = []
		reward_length_list = []		
		reward_mag = df['reward_mag'].unique()
		for reward_outcome in reward_mag:
			if reward_outcome == 0:
				continue
			df_reward = df[df['reward_mag'] == reward_outcome]
			reward_mag_list.append(np.mean(df_reward['reward_drops']))
			reward_length_list.append(np.mean(df_reward['reward_length']))
			reward_freq_list.append(np.mean(df_reward['reward_prob']))
		airpuff_mag_list = []
		airpuff_freq_list = []				
		airpuff_mag = df['airpuff_mag'].unique()
		for airpuff_outcome in airpuff_mag:
			if airpuff_outcome == 0:
				continue
			df_airpuff = df[df['airpuff_mag'] == airpuff_outcome]
			airpuff_mag_list.append(np.mean(df_airpuff['airpuff_pulses']))
			airpuff_freq_list.append(np.mean(df_airpuff['airpuff_prob']))
		self.reward_outcome_params['reward_drops'] = sorted(reward_mag_list, reverse=True)
		self.reward_outcome_params['reward_freq'] = sorted(reward_freq_list, reverse=True)
		self.reward_outcome_params['reward_length'] = sorted(reward_length_list, reverse=True)
		self.airpuff_outcome_params['airpuff_pulses'] = sorted(airpuff_mag_list, reverse=True)
		self.airpuff_outcome_params['airpuff_freq'] = sorted(airpuff_freq_list, reverse=True)

	def behavior_summary(self, behavioral_code_dict):
		df = self.df
		OUTCOME_SELECTED = [0,9]
		# attempts per min
		session_time = self.session_time
		session_time_min = session_time*60
		total_attempts_min = round(len(df)/session_time_min, 2)
		self.total_attempts_min = total_attempts_min
		# total initiated trials
		df_choice = df.loc[df['error_type'].isin(OUTCOME_SELECTED)]
		prop_trials_initiated = round(len(df_choice)/len(df), 2)
		self.prop_trials_initiated = prop_trials_initiated
		# total correct trials after CS presented
		cs_on_index = [index for index in behavioral_code_dict.keys() if behavioral_code_dict[index] == 'CS On'][0]
		session_df_CS_presented = df[df['behavioral_code_markers'].apply(lambda x: cs_on_index in x)]
		self.CS_on_trials = len(session_df_CS_presented)
		CS_on_correct = session_df_CS_presented['correct'].tolist()
		perf_CS_on = np.sum(CS_on_correct)/len(CS_on_correct)
		perf_CS_on_round = round(perf_CS_on, 2)
		self.prop_correct_CS_on = perf_CS_on_round