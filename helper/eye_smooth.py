import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.gridspec import GridSpec

def smooth_eye_data(trial):
	# 1. Look for 1000 Hz sampling (unlikely)
	# 2. Downsample to 500 Hz (may already start here)
	# 3. Look for double samples
	# 4. Look for missed samples
	# 		- Find data where acceleration is behind physiological thresholds
	# 5. Find out if the trial starts on a saccade; if so, nan that data
	# 6. Find “spikes where the eye signal quickly moves away from and then back to the same point. These spikes are typically attributed to corneal loss
	# 7. Smooth the data
	# 8. Remove blinks
	# 9. Remove data is “too short”
	# 10. Super-sample this data to 1000 Hz
	eye_x, eye_y = trial['eye_x'], trial['eye_y']
	print('Max (X):', min(eye_x))
	print('Max (Y):', min(eye_y))
	pupil = trial['eye_pupil']
	photodiode = trial['photodiode']
	trial_length = trial['End Trial']
	behavior_code_markers = trial['behavioral_code_markers']
	behavior_code_times = trial['behavioral_code_times']

	fig = plt.figure(figsize=(16, 8))
	gs = GridSpec(nrows=4, ncols=2)
	ax0 = fig.add_subplot(gs[0, 0])
	ax1 = fig.add_subplot(gs[1, 0])
	ax2 = fig.add_subplot(gs[2, 0])
	ax3 = fig.add_subplot(gs[3, 0])
	ax4 = fig.add_subplot(gs[:, 1])
	fig.subplots_adjust(top=0.95)
	fig.suptitle('Trial {}'.format(trial['trial_num']), y=0.98)

	eye_x_even = eye_x[::2] # even  - start at the beginning at take every second item
	eye_x_odd = eye_x[1::2] # odd - start at second item and take every second item

	if len(eye_x_even) == len(eye_x_odd):
		pass
	elif len(eye_x_even) > len(eye_x_odd):
		eye_x_odd = np.append(eye_x_odd, eye_x_even[-1])
	elif len(eye_x_even) < len(eye_x_odd):
		eye_x_even = np.append(eye_x_even, eye_x_odd[-1])

	eye_x_diff = eye_x_odd-eye_x_even
	zero_indices = np.where(eye_x_diff == 0)[0]
	nonzero_indices = np.nonzero(eye_x_diff)[0]
	ax0.scatter(zero_indices, [1]*len(zero_indices), s=2)
	ax0.scatter(nonzero_indices, [0]*len(nonzero_indices), s=2, alpha=0.2)
	ax1.scatter(zero_indices, eye_x[zero_indices], s=2)
	ax1.scatter(nonzero_indices, eye_x[nonzero_indices], s=2, alpha=0.2)
	ax1.set_ylabel('Eye X')
	ax2.scatter(zero_indices, eye_y[zero_indices], s=2)
	ax2.scatter(nonzero_indices, eye_y[nonzero_indices], s=2, alpha=0.2)
	ax2.set_ylabel('Eye Y')
	ax3.scatter(zero_indices, pupil[zero_indices], s=2)
	ax3.scatter(nonzero_indices, pupil[nonzero_indices], s=2, alpha=0.2)
	ax3.set_ylabel('Pupil')
	ax4.scatter(eye_x[zero_indices], eye_y[zero_indices], s=2)
	ax4.scatter(eye_y[nonzero_indices], eye_y[nonzero_indices], s=2, alpha=0.2)
	ax4.set_xlim([-20,20])
	ax4.set_ylim([-20,20])
	ax4.set_xlabel('Eye X')
	ax4.set_ylabel('Eye Y')
	fig.tight_layout()
	plt.show()