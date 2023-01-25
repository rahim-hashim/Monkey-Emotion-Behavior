import os
import sys
import cv2
import pickle
import numpy as np
from tqdm.auto import tqdm
from datetime import datetime, timedelta

def closest_timestamp(timestamp, eventcode, list_timestamps):
		"""
		closest_timestamp looks through a list of datetime objects
		to find the one that is closest to a specified datetime

		Args
			- timestamp (datetime): the specified datetime that we want to find the closest datetime to
			- eventcode (str): for printing purposes (i.e. 'trial start')
			- list_timestamps (list): list of datetimes that you go through to find the one that is closest to timestamp

		Returns
			- res (datetime): the closest datetime in the list of datetimes
		"""
		if list_timestamps:
				res = min(list_timestamps, key=lambda sub: abs(sub - timestamp))
		else:
				sys.exit('Missing IMAGE TIMESTAMP FILES')
	
		# printing result
		if eventcode:
				pass
		return res

def timestamp_image_formatter(timestamp_image_file):
		"""
		timestamp_image_formatter splits the t0 t1 and t2 .csv files
		and formats specifically the second element (hard coded) to a datetime

		Args
			- timestamp_image_file: file with comma-delimited lines (columns=2)
			
		Returns
			- timestamp_images_datetime (list): a list of converted datetimes
		"""
		timestamp_images = timestamp_image_file.readlines()
		# Split frame timestamps (comma-delimited, \n trailing)
		timestamp_images_formatted = list(map(lambda line: line.split(',')[1].strip(),
																											timestamp_images))
		# Convert to datetime
		timestamp_images_datetime = list(map(lambda img: datetime.strptime(img.strip(), "%Y-%m-%d %H:%M:%S.%f"),
																											timestamp_images_formatted))
		return timestamp_images_datetime

def str_to_datetime(timestamp_string):
	"""
	Cleans the timestamp string and converts it to a datetime 
	object with the format: %Y-%m-%d %H:%M:%S.%f
	"""
	timestamp_string = timestamp_string.strip()
	if '.' not in timestamp_string:
		timestamp_string += '.000000'
	timestamp_datetime = datetime.strptime(timestamp_string, "%Y-%m-%d %H:%M:%S.%f")
	return timestamp_datetime

def write_log(log_file, trial_index, content):
	trial_str = str(trial_index)
	if content == 'error':
		error_str = ','.join([trial_str,'','', ''])
		log_file.write(error_str + '\n')
	else:
		content_list = [trial_str] + list(map(str, content))
		content_str = ','.join(content_list)
		log_file.write(content_str + '\n')

def img_to_vid(trial, 
							 delay_only, 											# if True, only delay period is included in video
							 trial_start_timestamps, 					# list of trial start timestamps
							 trial_end_timestamps, 						# list of trial end timestamps
							 IMAGES_FOLDER, VIDEO_SAVE_PATH,  # save folders
							 DATE, MONKEY,      							# experiment parameters
							 cam_name, images_cam_list, 			# images folders
							 timestamp_images_datetime, 			# image timestamps
							 timestamp_image_file_list, 			# image timestamp files
							 specified_folder_path_list,			# image timestamp lists
							 log_file):								# log file
	"""
	Creates videos for each trial
	"""

	trial_index = int(trial['trial_num']) - 1
	trial_start_specified = trial_start_timestamps[trial_index]
	trial_start_datetime = str_to_datetime(trial_start_specified)
	trial_end_specified = trial_end_timestamps[trial_index]
	trial_end_datetime = str_to_datetime(trial_end_specified)

	# Segments trial for only delay period
	print('Trial Number: {}'.format(trial_index+1))

	if delay_only:
		if trial['correct'] == 1:
			delay_start = trial['Trace Start']
			delay_end = trial['Trace End']
			trial_start_segment_datetime = trial_start_datetime + timedelta(milliseconds=delay_start)
			trial_end_segment_datetime = trial_start_datetime + timedelta(milliseconds=delay_end)
		else:
			print('  Subject errored, skipping trial.')
			video_name = np.nan
			log_file = write_log(log_file, trial_index, 'error')
			return video_name 
	else:
		trial_start_segment_datetime = trial_start_datetime
		trial_end_segment_datetime = trial_start_datetime
	print('   Start: {}'.format(trial_start_segment_datetime))
	print('   End:   {}'.format(trial_end_segment_datetime))

	# Frames timestamp data
	min_dist_timestamp_list_start = []
	min_dist_timestamp_list_end = []

	# find the frame with the closest timestamp to trial start (or delay start for each trial)
	min_dist_timestamp_start = closest_timestamp(trial_start_segment_datetime, 'trial start', timestamp_images_datetime)
	min_dist_timestamp_list_start.append(min_dist_timestamp_start)
	min_dist_timestamp_end = closest_timestamp(trial_end_segment_datetime, 'trial end', timestamp_images_datetime)
	min_dist_timestamp_list_end.append(min_dist_timestamp_end)

	# If multiple session files (i.e. 20220902_Aragorn_behave.h5, 20220902_Aragorn_behave (1).h5...)
	# then select the session that has the closest timestamps to the specified trial
	min_dist_session = closest_timestamp(trial_start_segment_datetime, '', min_dist_timestamp_list_start)
	session_index = 0
	if min_dist_session == min_dist_timestamp_list_start[0]:
		session_closest_timestamp = specified_folder_path_list[0]
	else:
		session_closest_timestamp = specified_folder_path_list[1]
		session_index = 1

	frame_timestamp_start = min_dist_timestamp_list_start[session_index]
	frame_timestamp_end = min_dist_timestamp_list_end[session_index]
	frame_datetimes = timestamp_image_file_list[session_index]
	images_cam = images_cam_list[session_index]

	# Find the index of the closest video frame timestamp 
	# to the start and end of the trial (or delay)
	frame_index_start = 0
	frame_index_end = 0
	for f_index, frame_datetime in enumerate(frame_datetimes):
		if frame_timestamp_start == frame_datetime:
			frame_index_start = f_index
		if frame_timestamp_end == frame_datetime:
			frame_index_end = f_index
	if frame_index_start == 0 or frame_index_end == 0:
		print('Trial start or Trial end frame index not found')
		video_name = np.nan
		write_log(log_file, trial_index, 'error')
		return video_name
	if frame_index_start >= frame_index_end:
		print('Trial start frame index is greater than or equal to Trial end frame index')
		video_name = np.nan
		write_log(log_file, trial_index, 'error')
		return video_name

	timestamp_diff = frame_timestamp_start - trial_start_segment_datetime
	log_content = [trial_start_segment_datetime, frame_timestamp_start , timestamp_diff]
	write_log(log_file, trial_index, log_content)
	frame_count = frame_index_end-frame_index_start
	length_trial = (frame_timestamp_end-frame_timestamp_start).total_seconds()
	frame_rate = round(frame_count/length_trial, 3)

	video_name = DATE + '_' + MONKEY + '_trial_' + str(trial_index) + '_' + cam_name + '.mp4'
	
	# Parse specified timestamps and recreate video
	frame = cv2.imread(os.path.join(session_closest_timestamp, images_cam[0]))
	height, width, layers = frame.shape

	image_order = []
	for i_index, image in enumerate(images_cam):
		num_frame = list(image.split('_'))[1] # check file format to make sure (i.e. Gandalf_XXXX_cam0.jpg)
		image_order.append(int(num_frame))

	zipped_list = zip(image_order, images_cam)
	sort_image_order = sorted(zipped_list)
	sorted_image_num = [element for element, _ in sort_image_order]
	sorted_image_order = [element for _, element in sort_image_order]

	correct_num_frames = np.arange(len(images_cam))

	selected_images = []
	# only adds specified images (by frame number) and eliminates duplicates
	for i_index, image in enumerate(sorted_image_order):
		filename_num = int(image.split('_')[1])
		if (filename_num >= frame_index_start) and \
					(filename_num <= frame_index_end) and \
					(image not in selected_images):
				selected_images.append(image)

	video_name = DATE + '_' + MONKEY + '_trial_' + str(trial_index) + '_' + cam_name + '.mp4'
	video_file_path = os.path.join(session_closest_timestamp,video_name)
	video_save_path = os.path.join(VIDEO_SAVE_PATH, video_name)
	fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
	video = cv2.VideoWriter(video_save_path, fourcc, frame_rate, (width,height))
	video_path = session_closest_timestamp
	for image in tqdm(selected_images, desc='Frame'):
		video.write(cv2.imread(os.path.join(session_closest_timestamp, image)))

	cv2.destroyAllWindows()
	video.release()
	return video_name

def generate_videos(df, path_obj, delay_only, num_cameras):

	TRIAL_TIMESTAMP_FILE = path_obj.VIDEO_PATH
	IMAGES_FOLDER = path_obj.VIDEO_PATH
	DATE = df['date'].iloc[0]
	MONKEY = df['subject'].iloc[0]
	VIDEO_SAVE_PATH = os.path.join(path_obj.VIDEO_PATH, MONKEY + '_20' + DATE + '_videos')
	# Make save directory if it doesn't exist
	if os.path.exists(VIDEO_SAVE_PATH) == False:
			print('Making save directory: {}'.format(VIDEO_SAVE_PATH))
			os.mkdir(VIDEO_SAVE_PATH)

	# Trial timestamp data
	print('\nLooking for TRIAL TIMESTAMP file(s)...')
	print('Directory for trial timestamp data: {}'.format(TRIAL_TIMESTAMP_FILE))

	start_file_str = MONKEY + '_' + DATE + '_tr_starts.txt'
	start_file_path = os.path.join(TRIAL_TIMESTAMP_FILE, start_file_str)
	end_file_str = MONKEY + '_' + DATE + '_tr_ends.txt'
	end_file_path = os.path.join(TRIAL_TIMESTAMP_FILE, end_file_str)
	print('    {}'.format(start_file_str))
	print('    {}'.format(end_file_str))

	try:
		start_file = open(start_file_path, 'r')
		end_file = open(end_file_path, 'r')
	except:
		sys.exit('Trial timestamp files not found')

	trial_start_timestamps = start_file.readlines()
	trial_end_timestamps = end_file.readlines()

	print('  Total Trials: {}'.format(len(trial_start_timestamps)))

	# Images data
	image_folder = []
	print('\nLooking for IMAGES files...')
	print('Directory for images files: {}'.format(IMAGES_FOLDER))
	for folder in os.listdir(IMAGES_FOLDER):
		if DATE in folder and MONKEY in folder and os.path.isdir(os.path.join(IMAGES_FOLDER, folder)):
			image_folder.append(folder)
	if image_folder == []:
		sys.exit('Images folder not found')

	for cam_num in range(num_cameras):
		cam_name = 'cam{}'.format(cam_num)
		specified_folder_path_list = []
		images_cam_list = []
		print('Finding images from image_folder for {}...'.format(cam_name))
		for specified_folder in image_folder:
			specified_folder_path = os.path.join(IMAGES_FOLDER, specified_folder)
			specified_folder_path_list.append(specified_folder_path)
			images_cam = [img for img in os.listdir(specified_folder_path) if img.endswith('{}.jpg'.format(cam_name))]
			images_cam_list.append(images_cam)
			print('  Images folder found - {}'.format(specified_folder_path_list))

		# Image timestamps
		timestamp_image_file_list = []
		print('Finding timestamps from image_folder for {}...'.format(cam_name))
		for specified_folder_path in specified_folder_path_list:
			image_timestamp_filename = MONKEY + '_t{}.txt'.format(cam_name[-1])
			image_timestamp_file = os.path.join(specified_folder_path, image_timestamp_filename)
			try:
				timestamp_image_file = open(image_timestamp_file, 'r')
				timestamp_images_datetime = timestamp_image_formatter(timestamp_image_file)
				timestamp_image_file_list.append(timestamp_images_datetime)
				print('  Image timestamps found - {}'.format(image_timestamp_file))
			except:
				pass

		# Log file
		log_file = open (os.path.join(VIDEO_SAVE_PATH, 'log_{}.txt'.format(cam_name)), 'w')
		log_file.write('# Logs for video files' + '\n')
		log_file.write('## trial_index, trial_start, frame_start, start_diff' + '\n')

		tqdm.pandas(desc='Trial Number') # tqdm pandas progress bar
		print('Starting video generation...')
		df[cam_name] = df.progress_apply(img_to_vid,
						delay_only=delay_only,
						trial_start_timestamps=trial_start_timestamps,
						trial_end_timestamps=trial_end_timestamps,
						IMAGES_FOLDER=IMAGES_FOLDER, 
						VIDEO_SAVE_PATH=VIDEO_SAVE_PATH,
						DATE=DATE,
						MONKEY=MONKEY,
						cam_name=cam_name,
						images_cam_list=images_cam_list,
						timestamp_images_datetime=timestamp_images_datetime,
						timestamp_image_file_list=timestamp_image_file_list,
						specified_folder_path_list=specified_folder_path_list,
						log_file=log_file, 
						axis=1)
		print('{} videos complete.'.format(cam_name))
		log_file.close()

	# dump pickle file
	with open (os.path.join(VIDEO_SAVE_PATH, 'session_df.pkl'), 'wb') as f:
		pickle.dump(df, f)

	return df