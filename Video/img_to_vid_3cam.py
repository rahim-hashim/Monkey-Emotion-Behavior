# Written by Rahim Hashim (2/1/22)
#
# Converts image files outputted
# by FLIR_Multicam to a video

# RG 20220405: Changed ouput format from AVI to MP4
# RH 20220422: Added check for missing/duplicate camera files
# 

import sys
import cv2
import os
import tqdm
import numpy as np
from datetime import datetime

DATE = '20220902'
MONKEY = 'Aragorn'

# for L6 computer
#TIMESTAMP_TRIAL_FOLDER = 'C:/Users/L6_00/Google Drive/Postdoc/Projects/SnMTS/data/SnMTS_v3/'
#TIMESTAMP_TRIAL_FOLDER = '/mnt/c/Users/L6_00/Google Drive/Postdoc/Projects/SnMTS/data/SnMTS_v3/'
#IMAGES_FOLDER = os.path.join(TIMESTAMP_TRIAL_FOLDER, 'images')

# for RH local 
TIMESTAMP_TRIAL_FOLDER = os.getcwd()

# Google Drive
# IMAGES_FOLDER = os.path.join(TIMESTAMP_TRIAL_FOLDER, 'images', 'analysis')

# Hard Drive
IMAGES_FOLDER = '/Volumes/LaCie/Video'
# TIMESTAMP_TRIAL_FOLDER = '/Volumes/LaCie/Video'

# Save path
VIDEO_SAVE_PATH = '/Users/rahimhashim/Desktop/Aragorn_20220902'

def closest_timestamp(timestamp, eventcode, list_timestamps):
		'''
		closest_timestamp looks through a list of datetime objects
		to find the one that is closest to a specified datetime

		Args
			- timestamp (datetime): the specified datetime that we want to find the closest datetime to
			- eventcode (str): for printing purposes (i.e. 'trial start')
			- list_timestamps (list): list of datetimes that you go through to find the one that is closest to timestamp

		Returns
			- res (datetime): the closest datetime in the list of datetimes
		'''
		if list_timestamps:
				res = min(list_timestamps, key=lambda sub: abs(sub - timestamp))
		else:
				sys.exit('Missing IMAGE TIMESTAMP FILES')
	
		# printing result
		if eventcode:
				print('      Nearest timestamp to {}: {}'.format(eventcode, str(res)))
		return res

def timestamp_image_formatter(timestamp_image_file):
		'''
		timestamp_image_formatter splits the t0 t1 and t2 .csv files
		and formats specifically the second element (hard coded) to a datetime

		Args
			- timestamp_image_file: file with comma-delimited lines (columns=2)
			
		Returns
			- timestamp_images_datetime (list): a list of converted datetimes
		'''
		timestamp_images = timestamp_image_file.readlines()
		# Split frame timestamps (comma-delimited, \n trailing)
		timestamp_images_formatted = list(map(lambda line: line.split(',')[1].strip(),
																											timestamp_images))
		# Convert to datetime
		timestamp_images_datetime = list(map(lambda img: datetime.strptime(img.strip(), "%Y-%m-%d %H:%M:%S.%f"),
																											timestamp_images_formatted))
		print('      Number of image timestamps found: {}'.format(len(timestamp_images)))
		return timestamp_images_datetime

def img_to_vid(trial_number_str):

		# Specify session
		print('Date selected: '+ DATE)
		print('Monkey selected: '+ MONKEY)

		# Trial timestamp data
		print('\nLooking for TRIAL TIMESTAMP file(s)...')
		print('Directory for trial timestamp data: {}'.format(TIMESTAMP_TRIAL_FOLDER))

		start_file_str = MONKEY + '_' + DATE[2:] + '_tr_starts.txt'
		start_file_path = os.path.join(TIMESTAMP_TRIAL_FOLDER, start_file_str)
		end_file_str = MONKEY + '_' + DATE[2:] + '_tr_ends.txt'
		end_file_path = os.path.join(TIMESTAMP_TRIAL_FOLDER, end_file_str)
		print('  {}'.format(start_file_str))
		print('  {}'.format(end_file_str))

		# Make save directory if it doesn't exist
		if os.path.exists(VIDEO_SAVE_PATH) == False:
				print('Making save directory: {}'.format(VIDEO_SAVE_PATH))
				os.mkdir(VIDEO_SAVE_PATH)

		try:
				start_file = open(start_file_path, 'r')
				end_file = open(end_file_path, 'r')
		except:
				sys.exit('Trial timestamp files not found')

		trial_start_timestamps = start_file.readlines()
		trial_end_timestamps = end_file.readlines()

		print('Total Trials: {}'.format(len(trial_start_timestamps)))
		# trial_number_str = input('Specify Trial Number (i.e. 1, 2, ...) ')
		try:
				trial_number = int(trial_number_str) - 1 # index by 1, 2, 3 (not 0, 1, 2)
				print('Trial specified: {}'.format(trial_number+1))
				# trial_start_specified = trial_start_timestamps[trial_number]
				# trial_start_datetime = datetime.strptime(trial_start_specified.strip(), "%Y-%m-%d %H:%M:%S.%f")
				trial_start_specified = trial_end_timestamps[trial_number-1]
				trial_start_datetime = datetime.strptime(trial_start_specified.strip(), "%Y-%m-%d %H:%M:%S.%f")
				print('  Trial start time: {}'.format(trial_start_datetime))
				# trial_end_specified = trial_end_timestamps[trial_number]
				# trial_end_datetime = datetime.strptime(trial_end_specified.strip(), "%Y-%m-%d %H:%M:%S.%f")
				trial_end_specified = trial_end_timestamps[trial_number]
				trial_end_datetime = datetime.strptime(trial_end_specified.strip(), "%Y-%m-%d %H:%M:%S.%f")
				print('  Trial end time: {}'.format(trial_end_datetime))
				print('  Trial length: {}'.format(trial_end_datetime-trial_start_datetime))
		except:
				sys.exit('Trial number specified in incorrect format') 

		# Images data
		print('\nLooking for IMAGES files...')
		image_folder = []
		for folder in os.listdir(IMAGES_FOLDER):
				if DATE in folder and MONKEY in folder:
						image_folder.append(folder)
		if image_folder == []:
				print('Date and Monkey combination not found in images folder')
				sys.exit()
		else:
				print('Image Files Found: {}'.format(image_folder))

		specified_folder_path_list = []
		images_cam0_list = []
		images_cam1_list = []
		images_cam2_list = []
		for specified_folder in image_folder:
				print('Specified session: {}'.format(specified_folder))
				specified_folder_path = os.path.join(IMAGES_FOLDER, specified_folder)
				specified_folder_path_list.append(specified_folder_path)
				print('  total images:', len(os.listdir(specified_folder_path)))
				images_cam0 = [img for img in os.listdir(specified_folder_path) if img.endswith("cam0.jpg")]
				images_cam0_list.append(images_cam0)
				images_cam1 = [img for img in os.listdir(specified_folder_path) if img.endswith("cam1.jpg")]
				images_cam1_list.append(images_cam1)
				images_cam2 = [img for img in os.listdir(specified_folder_path) if img.endswith("cam2.jpg")]
				images_cam2_list.append(images_cam2)
				print('    images (cam0 only):', len(images_cam1))
				print('    images (cam1 only):', len(images_cam1))
				print('    images (cam2 only):', len(images_cam2))
		images_cam_list = [images_cam0_list, images_cam1_list, images_cam2_list]
		# Frames timestamp data
		min_dist_timestamp_list_t0_start = []
		min_dist_timestamp_list_t0_end = []
		timestamp_image_file_t0_list = []
		min_dist_timestamp_list_t1_start = []
		min_dist_timestamp_list_t1_end = []
		timestamp_image_file_t1_list = []
		min_dist_timestamp_list_t2_start = []
		min_dist_timestamp_list_t2_end = []
		timestamp_image_file_t2_list = []
		print('\nLooking for IMAGE TIMESTAMP file(s)')
		for specified_folder_path in specified_folder_path_list:
				print('\n  Session: {}'.format(specified_folder_path.split('/')[1]))
				t0_file = os.path.join(specified_folder_path, MONKEY + '_t0.txt')
				t1_file = os.path.join(specified_folder_path, MONKEY + '_t1.txt')
				t2_file = os.path.join(specified_folder_path, MONKEY + '_t2.txt')
				# t0
				try:
						timestamp_image_file_t0 = open(t0_file, 'r')
						print('    t0 frames timestamp file: {}'.format(t0_file))
						timestamp_images_datetime = timestamp_image_formatter(timestamp_image_file_t0)
						min_dist_timestamp_t0_start = closest_timestamp(trial_start_datetime, 'trial start', timestamp_images_datetime)
						min_dist_timestamp_list_t0_start.append(min_dist_timestamp_t0_start)
						min_dist_timestamp_t0_end = closest_timestamp(trial_end_datetime, 'trial end', timestamp_images_datetime)
						min_dist_timestamp_list_t0_end.append(min_dist_timestamp_t0_end)
						print('      t0 trial length: {}'.format(min_dist_timestamp_t0_end-min_dist_timestamp_t0_start))
						timestamp_image_file_t0_list.append(timestamp_images_datetime)
				except:
						print('    t0 frames timestamp files not found: {}'.format(t0_file))
				# t1
				try:
						timestamp_image_file_t1 = open(t1_file, 'r')
						print('    t1 frames timestamp file: {}'.format(t1_file))
						timestamp_images_datetime = timestamp_image_formatter(timestamp_image_file_t1)
						min_dist_timestamp_t1_start = closest_timestamp(trial_start_datetime, 'trial start', timestamp_images_datetime)
						min_dist_timestamp_list_t1_start.append(min_dist_timestamp_t1_start)
						min_dist_timestamp_t1_end = closest_timestamp(trial_end_datetime, 'trial end', timestamp_images_datetime)
						min_dist_timestamp_list_t1_end.append(min_dist_timestamp_t1_end)
						print('      t1 trial length: {}'.format(min_dist_timestamp_t1_end-min_dist_timestamp_t1_start))
						timestamp_image_file_t1_list.append(timestamp_images_datetime)
				except:
						print('    t1 frames timestamp files not found: {}'.format(t1_file))
				# t2
				try:
						timestamp_image_file_t2 = open(t2_file, 'r')
						print('    t2 frames timestamp file: {}'.format(t2_file))
						timestamp_images_datetime = timestamp_image_formatter(timestamp_image_file_t2)
						min_dist_timestamp_t2_start = closest_timestamp(trial_start_datetime, 'trial start', timestamp_images_datetime)
						min_dist_timestamp_list_t2_start.append(min_dist_timestamp_t2_start)
						min_dist_timestamp_t2_end = closest_timestamp(trial_end_datetime, 'trial end', timestamp_images_datetime)
						min_dist_timestamp_list_t2_end.append(min_dist_timestamp_t2_end)
						print('      t2 trial length: {}'.format(min_dist_timestamp_t2_end-min_dist_timestamp_t2_start))
						timestamp_image_file_t2_list.append(timestamp_images_datetime)
				except:
						print('    t2 frames timestamp files not found: {}'.format(t2_file))

		# Matching timestamps data
		print('\nMatching TRIAL TIMESTAMP and IMAGE TIMESTAMP files')
		min_dist_timestamp_list_start = [min_dist_timestamp_list_t0_start, min_dist_timestamp_list_t1_start, min_dist_timestamp_list_t2_start]
		min_dist_timestamp_list_end = [min_dist_timestamp_list_t0_end, min_dist_timestamp_list_t1_end, min_dist_timestamp_list_t2_end]
		cam_names = ['cam0', 'cam1', 'cam2']
		timestamp_image_file_cam_list = [timestamp_image_file_t0_list, timestamp_image_file_t1_list, timestamp_image_file_t2_list]
		for cam_index, min_dist_timestamp_list_cam_start in enumerate(min_dist_timestamp_list_start):
			min_dist_session = closest_timestamp(trial_start_datetime, '', min_dist_timestamp_list_cam_start)
			session_index = 0
			if min_dist_session == min_dist_timestamp_list_cam_start[0]:
					session_closest_timestamp = specified_folder_path_list[0]
			else:
					session_closest_timestamp = specified_folder_path_list[1]
					session_index = 1
			print('  Session with closest trial start timestamp: {}'.format(session_closest_timestamp.split('/')[-1]))

			frame_timestamp_start = min_dist_timestamp_list_cam_start[session_index]
			frame_timestamp_end = min_dist_timestamp_list_end[cam_index][session_index]
			frame_datetimes = timestamp_image_file_cam_list[cam_index][session_index]
			images_cam = images_cam_list[cam_index][session_index]

			frame_index_start = 0
			frame_index_end = 0

			for f_index, frame_datetime in enumerate(frame_datetimes):
					if frame_timestamp_start == frame_datetime:
							frame_index_start = f_index
							print('    Trial Start Frame Index: {}'.format(frame_index_start))
					if frame_timestamp_end == frame_datetime:
							frame_index_end = f_index
							print('    Trial End Frame Index: {}'.format(frame_index_end))
			if frame_index_start == 0 or frame_index_end == 0:
					sys.exit('Trial start or Trial end frame index not found')

			print('\nCalculating Frame Rate')
			frame_count = frame_index_end-frame_index_start
			length_trial = (frame_timestamp_end-frame_timestamp_start).total_seconds()
			frame_rate = round(frame_count/length_trial, 3)
			print('  {} frames/sec'.format(frame_rate))

			# Generating video with specified frame_index_start and frame_index_end
			print('\nGenerating VIDEO file')

			# Parse specified timestamps and recreate video
			print('\n  {}'.format(cam_names[cam_index]))
			video_name = DATE + '_' + MONKEY + '_trial_' + trial_number_str + '_' + cam_names[cam_index] + '.mp4'
			frame = cv2.imread(os.path.join(session_closest_timestamp, images_cam[0]))
			height, width, layers = frame.shape

			print('    HxWxL: {}x{}x{}'.format(height, width, layers))

			image_order = []
			for i_index, image in enumerate(images_cam):
					num_frame = list(image.split('_'))[1] # check file format to make sure (i.e. Gandalf_XXXX_cam0.jpg)
					image_order.append(int(num_frame))

			zipped_list = zip(image_order, images_cam)
			sort_image_order = sorted(zipped_list)
			sorted_image_num = [element for element, _ in sort_image_order]
			sorted_image_order = [element for _, element in sort_image_order]

			correct_num_frames = np.arange(len(images_cam))
			# print(set(sorted_image_num) ^ set(correct_num_frames))

			selected_images = []
			# only adds specified images (by frame number) and eliminates duplicates
			for i_index, image in enumerate(sorted_image_order):
					filename_num = int(image.split('_')[1])
					if (filename_num >= frame_index_start) and \
									(filename_num <= frame_index_end) and \
									(image not in selected_images):
							selected_images.append(image)

			print('    Number of frames: {}'.format(len(selected_images)))

			print('    WRITING VIDEO...')
			video_file_path = os.path.join(session_closest_timestamp,video_name)
			video_save_path = os.path.join(VIDEO_SAVE_PATH, video_name)
			#video = cv2.VideoWriter(video_file_path, 0, frame_rate, (width,height))
			fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
			video = cv2.VideoWriter(video_save_path, fourcc, frame_rate, (width,height))
			video_path = session_closest_timestamp
			for image in tqdm.tqdm(selected_images):
					video.write(cv2.imread(os.path.join(session_closest_timestamp, image)))

			print('    VIDEO complete.') 
			print('    Path: {}'.format(VIDEO_SAVE_PATH))
			print('    Video name: {}'.format(video_name))
			cv2.destroyAllWindows()
			video.release()

trial_start = 0
trial_end = 2			
for i in range(trial_start, trial_end):
	img_to_vid(str(i))