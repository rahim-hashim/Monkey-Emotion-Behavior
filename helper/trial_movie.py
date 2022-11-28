import os
import cv2
import random
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from itertools import count
from IPython import display
import ruptures as rpt
import matplotlib.animation as animation

from eye_smooth import smooth_eye_data

def write_times(session_obj, session_df):
	'''
	writes start and end times for each trial in session
	to files <monkey>_<date>_tr_<starts|ends>.txt
	'''
	monkey = session_obj.monkey
	print('Writing trial start and end times.')
	for date in session_df['date'].unique():
		start_file_name = monkey+'_'+date+'_tr_starts.txt'
		start_file_path = os.path.join(session_obj.video_path, start_file_name)
		end_file_name = monkey+'_'+date+'_tr_ends.txt'
		end_file_path = os.path.join(session_obj.video_path, end_file_name)
		with open(start_file_path, 'w') as f:
			start_times = list(map(str,session_df['trial_datetime_start'].tolist()))
			for trial in start_times:
				f.write(trial+'\n')
			print('  Start Times Path: {}'.format(start_file_name))
		with open(end_file_path, 'w') as f:
			end_times = list(map(str,session_df['trial_datetime_end'].tolist()))
			for trial in end_times:
				f.write(trial+'\n')
			print('  End Times Path: {}'.format(end_file_name))

def select_trial(session_df, session_obj):

	trial_selected = int(input('Specify Trial Number (i.e. 1, 2, ...) '))

	VIDEO_SUFFIX = 'Aragorn_20220421-1331'
	VIDEO_PATH = os.path.join(session_obj.video_path, 'images', VIDEO_SUFFIX)
	VIDEO_NAME = '20220421_Aragorn_trial_{}_cam1.mp4'.format(trial_selected)
	VIDEO = os.path.join(VIDEO_PATH, VIDEO_NAME)

	trial_selected -= 1 # Trials indexed at 1 to match img_to_vid.py

	print('Reading Video: {}'.format(VIDEO_NAME))
	video_capture = cv2.VideoCapture(VIDEO)
	# no video found
	if (video_capture.isOpened()== False):
		print('Error opening video stream or file')
		video_pixel_avg = np.zeros(len(session_df['photodiode'].iloc[trial_selected]))
	# video found
	else:
		video_pixel_avg = []
		while(video_capture.isOpened()):
			ret, frame = video_capture.read()
			if ret == True:
				video_pixel_avg.append(np.mean(frame))

	datetime_start = session_df['trial_datetime_start'].iloc[trial_selected]
	datetime_end = session_df['trial_datetime_end'].iloc[trial_selected]
	print('  Start datetime: {}'.format(datetime_start))
	print('  End datetime: {}'.format(datetime_end))
	trial_lick = session_df['lick'].iloc[trial_selected]
	trial_photodiode = session_df['photodiode'].iloc[trial_selected]
	eye_x = session_df['eye_x'].iloc[trial_selected]
	eye_y = session_df['eye_y'].iloc[trial_selected]
	x = np.arange(len(trial_lick))
	f, axarr = plt.subplots(4, 1)
	axarr[0].plot(x, trial_lick)
	axarr[0].set_title('Lick')
	lick_diff = [0] + list(np.diff(trial_lick))
	lick_diff_sig = [x_index for x_index, x in enumerate(lick_diff) if abs(x) > 2.5]
	# algo1 = rpt.Pelt(model="rbf").fit(trial_lick)
	# change_location1 = algo1.predict(pen=10)
	for c_index, change_point in enumerate(lick_diff_sig):
			axarr[0].axvline(change_point,lw=1, color='red', alpha=0.4)
			axarr[0].text(change_point, 5.2, s=change_point, color='red', alpha=0.4, size=6)
	axarr[1].plot(x, trial_photodiode)
	axarr[1].set_title('ML Photodiode')
	axarr[2].plot(range(len(video_pixel_avg)), video_pixel_avg)
	axarr[2].set_title('Video Photodiode')
	axarr[3].plot(range(len(eye_x)), eye_x, label='x')
	axarr[3].plot(range(len(eye_y)), eye_y, label='y')
	axarr[3].set_title('Eye Data')
	axarr[3].legend()
	plt.tight_layout()
	plt.show()
	plt.close()

	smooth_eye_data(session_df.iloc[trial_selected])

	#############

def anim_text(trial_lick):
	x = []
	y = []
	f, ax = plt.subplots()
	
	def animate(i):
		pt = trial_lick.pop(0)
		x.append(i)
		y.append(pt)

		ax.clear()
		ax.plot(x,y)
		ax.set_ylim([0,5])
	
	ani = animation.FuncAnimation(f, animate, frames=len(trial_lick)-1, interval=1, repeat=False)
	# f = 'test.gif' 
	# writergif = animation.PillowWriter(fps=30) 
	# ani.save(f, writer=writergif)

	# anim_text(list(trial_lick))

	# from trial_movie import trial_movie
	# trial_filename = 'trial_{}_lick_data.txt'.format(trial_selected)
	# with open(trial_filename, 'w') as f:
	# 	for f_index, frame in enumerate(trial):
	# 		# each frame is 1ms
	# 		time_change = datetime.timedelta(milliseconds=1*f_index)
	# 		frame_ms = trial_datetime_start + time_change
	# 		f.write('{}, {}\n'.format(frame, frame_ms))

# x1=[]
# y1=[]
# i1 = count()
# def animate1(j):
# 		t=next(i1)
# 		x1.append(2*t)
# 		y1.append(np.sin(t))
# 		plt.cla()
# 		plt.plot(x1,y1)

# def trial_movie(lick_data):
# 	animation_2 = animation.FuncAnimation(plt.gcf(),animate1,interval=50)
# 	video_2 = animation_2.to_html5_video()
# 	html_code_2 = display.HTML(video_2)
# 	display.display(html_code_2)
# 	plt.tight_layout()
# 	plt.show()