import re
import numpy as np
from tqdm.auto import tqdm
from collections import defaultdict
from datetime import datetime, timedelta
from time_processing import calculate_end_time

def stimulus_parser(stimulus, stimuli_dict, session_dict):
	'''Parses out parameters for each stimulus set for each trial config

  Parameters
  ----------
	session : .h5 group object
		contains 
	stimuli_dict : Dict
		all specified stimuli info will be inputted
	session_dict: Dict 
		dictionary containing all specified session data

  Returns
  -------
	stimuli_dict : Dict
		all specified stimuli info will be inputted
	session_dict: Dict 
		dictionary containing all specified session data
	'''
	stimuli_name = ''
	# stimuli type = pic
	try:
			stimuli_type = stimulus['1'][...].tolist().decode()
			#stimuli_dict['stimuli_type'].append(stimuli_type)
			stimuli_string = stimulus['2'][...].tolist().decode()
			stimuli_name = stimuli_string.split('\\')[-1].split('.')[0]
			if '_fix' in stimuli_name:
				pass
			else:
				x_pos = stimulus['3'][...][0]
				y_pos = stimulus['4'][...][0]
				session_dict['stimuli_name'].append(stimuli_name) # name
				session_dict['x_pos'].append(x_pos) # x-position
				session_dict['y_pos'].append(y_pos) # y-position
	except:
		pass
	return(stimuli_dict, session_dict)

def session_parser(session, trial_list, trial_record, date_input, monkey_input):
	'''Parses out session data

  Parameters
  ----------
	session : .h5 file
		specified session for parsing
	trial_list : list
		list of trials within session

  Returns
  -------
	session_dict: Dict 
		dictionary containing all specified session data
	'''
	session_dict = defaultdict(list)

	# date (and handling for multiple sessions)
	session_dict['date'] = date_input
	session_str = str(session)
	session_str_num = re.search(r'\((.*?)\)',session_str).group(1)
	if session_str_num.isnumeric():
		session_dict['session_num'] = int(session_str_num)
	else:
		session_dict['session_num'] = int(0)

	# monkey
	session_dict['subject'] = monkey_input
	
	# error code mapping
	error_dict = defaultdict(str)
	try:
		for error_code in list(trial_record['TaskInfo']['TrialErrorCodes'].keys()):
			error_val = str(int(error_code)+1) # ML messes up TrialErrorCodes mapping to be 1-based
			# [...] returns scalar values from .h5 branches
			try:
				error_codes_val = trial_record['TaskInfo']['TrialErrorCodes'][error_val][...].tolist().decode()
				# take off leading b'
				error_dict[error_code] = error_codes_val
			except KeyError:
				pass # fix .h5 error code mapping

		# behavioral code mapping
		behavioral_code_dict = defaultdict(str)
		behavioral_numbers = list(map(int, trial_record['TaskInfo']['BehavioralCodes']['CodeNumbers'][0]))
		behavioral_code_keys = list(trial_record['TaskInfo']['BehavioralCodes']['CodeNames'].keys())
		behavioral_names = []
		for bev_key in behavioral_code_keys:
			behavioral_names.append(trial_record['TaskInfo']['BehavioralCodes']['CodeNames'][bev_key][...].tolist().decode())
		for b_index, behavioral_code in enumerate(behavioral_numbers):
			try:
				behavioral_code_dict[behavioral_code] = behavioral_names[b_index]
			except KeyError:
				pass # fix .h5 behavioral code mapping
	except:
		behavioral_code_dict = defaultdict(str)
		pass

	try:
		stim_container = trial_record['User']['stim_list'] # ML user-generated variables
		stim_list = stim_container.keys()
		reward_container = trial_record['User']['reward'] # ML user-generated variables
		airpuff_container = trial_record['User']['airpuff'] # ML user-generated variables
	except:
		pass

	# trial_list is ordered already (Trial1...TrialN) but we should put in some checks
	# to make sure that it holds in all cases
	for t_index, trial in enumerate(trial_list):

		# all trial data
		trial_data = session['ML'][trial]

		# trial number
		trial_num = list(trial_data['Trial'][0]) # starts at Trial 1...Trial N
		session_dict['trial_num'].append(int(trial_num[0]))

		# block
		block = int(trial_data['Block'][()][0][0])
		session_dict['block'].append(block)

		# condition
		condition = int(trial_data['Condition'][()][0][0])
		session_dict['condition'].append(condition)

		trial_result = int(trial_data['TrialError'][()][0][0])
		# correct trial
		if trial_result == 0:
			session_dict['correct'].append(1)
			session_dict['error'].append(0)
		# error trial
		else:
			session_dict['correct'].append(0)
			session_dict['error'].append(1)

		# error code mapping
		#   - error_dict[0]     = 'correct'
		#   - error_dict[{1-9}] = '<error_type>'
		session_dict['error_type'].append(int(trial_result))

		# behavioral codes
		behavioral_code_markers = np.array(trial_data['BehavioralCodes']['CodeNumbers'][0])
		behavioral_code_times = np.array(trial_data['BehavioralCodes']['CodeTimes'][0])
		session_dict['behavioral_code_markers'].append(list(map(int,behavioral_code_markers)))
		session_dict['behavioral_code_times'].append(behavioral_code_times)

		# stimuli info
		stimuli_attribute = trial_data['TaskObject']['Attribute']
		stimuli_dict = defaultdict(list)
		# all hard coded by MonkeyLogic and therefore here as well
		try:  # list of stimuli in stimuli_attribute
			test_for_list = stimuli_attribute['1'] 
			for stimulus in stimuli_attribute:
				stimuli_dict, session_dict = stimulus_parser(stimuli_attribute[stimulus], stimuli_dict, session_dict)
		except: # one stimuli in stimuli_attribute
			stimuli_dict, session_dict = stimulus_parser(stimuli_attribute, stimuli_dict, session_dict)
		if 'stim_list' in locals(): # experiment contains user-generated variable TrialRecord.User.stim_container
			for stimulus in stim_list:
				# exclude fix (no degree value)
				if stimulus == 'fix':
					continue
		if 'reward_container' in locals():
			reward = int(reward_container['reward'][t_index])
			session_dict['reward'].append(reward)
			reward_prob = float(reward_container['reward_prob'][t_index])
			session_dict['reward_prob'].append(reward_prob)
			try: # new fields in reward_container
				reward_mag = float(reward_container['reward_mag'][t_index])
				session_dict['reward_mag'].append(reward_mag)
				reward_drops = float(reward_container['drops'][t_index])
				session_dict['reward_drops'].append(reward_drops)		
				reward_length = float(reward_container['length'][t_index])
				session_dict['reward_length'].append(reward_length)	
			except:
				pass
		if 'airpuff_container' in locals():
			airpuff = int(airpuff_container['airpuff'][t_index])
			session_dict['airpuff'].append(airpuff)
			airpuff_prob = float(airpuff_container['airpuff_prob'][t_index])
			session_dict['airpuff_prob'].append(airpuff_prob)
			try: # new fields in airpuff_container
				airpuff_mag = float(airpuff_container['airpuff_mag'][t_index])
				session_dict['airpuff_mag'].append(airpuff_mag)
				num_pulses = float(airpuff_container['num_pulses'][t_index])
				session_dict['airpuff_pulses'].append(num_pulses)
				airpuff_L_side = float(airpuff_container['L_side'][t_index])
				session_dict['airpuff_side_L'].append(airpuff_L_side)
				airpuff_R_side = float(airpuff_container['R_side'][t_index])
				session_dict['airpuff_side_R'].append(airpuff_R_side)
			except:
				pass
		# eye data
		x = np.array(trial_data['AnalogData']['Eye'])
		eye_data = x.view(np.float64).reshape(x.shape+(-1,))
		session_dict['eye_x'].append(eye_data[0].flatten())
		session_dict['eye_y'].append(eye_data[1].flatten())
		# session_dict['eye_x'].append(eye_data[0])
		# session_dict['eye_y'].append(eye_data[1])

		# pupil data
		x = np.array(trial_data['AnalogData']['EyeExtra'])
		try:
			session_dict['eye_pupil'].append(x[0])
		except:
			pass # no pupil data

		# joystick data
		x = np.array(trial_data['AnalogData']['Joystick'])
		try:
			joystick_data = x.view(np.float64).reshape(x.shape+(-1,))
			session_dict['joystick_x'].append(joystick_data[0])
			session_dict['joystick_y'].append(joystick_data[1])
		except:
			pass # no joystick data

		# lick data
		x = np.array(trial_data['AnalogData']['General']['Gen1'])
		session_dict['lick'].append(x[0])

		# reward data
		# x = np.array(trial_data['VariableChanges'])

		# photodiode data
		x = np.array(trial_data['AnalogData']['PhotoDiode'])
		session_dict['photodiode'].append(x[0])

		# trial start time (relative to session start)
		trial_start_time = float(trial_data['AbsoluteTrialStartTime'][()][0][0])
		session_dict['trial_start'].append(trial_start_time)
		
		# trial start time (absolute)
		length_trial = len(x[0])

		start_datetime, end_datetime = calculate_end_time(trial_data['TrialDateTime'][()], length_trial)

		session_dict['trial_datetime_start'].append(start_datetime)
		session_dict['trial_datetime_end'].append(end_datetime)


	# pop all non-equal keys
	num_trials = len(session_dict['trial_num'])
	for key in list(session_dict.keys()):
		# excluded from checks
		if key in ['date', 'subject']:
			continue
		try:
			if len(session_dict[key]) != num_trials:
				session_dict.pop(key)
				print('  {} removed from session_dict'.format(key))
		except:
			pass

	print('    Correct trials: {}'.format(np.sum(session_dict['correct'])))
	print('    Errored trials: {}'.format(np.sum(session_dict['error'])))

	return session_dict, error_dict, behavioral_code_dict