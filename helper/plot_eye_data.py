import math 
import numpy as np
import pandas as pd
import matplotlib.colors
from operator import itemgetter
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import defaultdict, OrderedDict

def plot_eye_data(session_df):
  import seaborn as sns

  trial_numbers = input('Enter trial numbers to plot (e.g. 1,2,3...{}): '.format(len(session_df)))
  row = session_df.iloc[int(trial_numbers)]
  trial_numbers = list(row.index)

  # correct origin, sample, target, distractor target_end
  delay_start = row['Trace Start']
  delay_end = row['Trace End']
  eye_x = row['eye_x'][delay_start:delay_end]
  eye_y = row['eye_y'][delay_start:delay_end]
  eye_data = zip(eye_x, eye_y)
  for i in range_len(eye_data):
    print(i, eye_data[i])
    if i == 10:
      break
  fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20,5), sharex=True, sharey=True)

  # Plotting Stimuli
  ax1.scatter(0, 0, s=ring_size, edgecolors='grey', facecolors='none')
  ax1.scatter(0, 0, s=fix_size, edgecolors='grey', facecolors='none')
  ax1.scatter(origin_1_x_pos, origin_1_y_pos, s=stim_size, facecolors='grey', edgecolors='grey')
  ax1.scatter(sample_1_x_pos, sample_1_y_pos, s=stim_size, facecolors='cyan', edgecolors='cyan')
  ax2.scatter(0, 0, s=ring_size, edgecolors='grey', facecolors='none')
  ax2.scatter(0, 0, s=fix_size, edgecolors='grey', facecolors='none')
  ax3.scatter(0, 0, s=ring_size, edgecolors='grey', facecolors='none')
  ax3.scatter(0, 0, s=fix_size, edgecolors='grey', facecolors='none')
  ax3.scatter(origin_2_x_pos, origin_2_y_pos, s=stim_size, facecolors='grey', edgecolors='grey')
  ax3.scatter(target_x_pos, target_y_pos, s=stim_size, facecolors='magenta', edgecolors='black', linewidth=2)
  ax3.scatter(distractor_x_pos, distractor_y_pos, s=stim_size, facecolors='magenta', edgecolors='magenta')

  trial_eye_data = eye_data[t_index]
  sample_plot = list(range(101, 105))
  delay_plot = list(range(105, 106))
  target_plot = list(range(106, 111))
  print('Trial', trial_numbers[t_index])
  print('  ', trial_eye_data.keys())
  last_event = max(list(trial_eye_data.keys()))
  for event_code in list(trial_eye_data.keys()):
    eye_x_trial = trial_eye_data[event_code]['x']
    eye_y_trial = trial_eye_data[event_code]['y']
    if event_code in sample_plot:
      ax1.plot(eye_x_trial, eye_y_trial)
    if event_code in delay_plot:
      ax2.plot(eye_x_trial, eye_y_trial)
    if event_code in target_plot:
      ax3.plot(eye_x_trial, eye_y_trial)
    if event_code == last_event: # where was his eye position in the last event before error
      print('max x:', max(eye_x_trial))
      print('max y:', max(eye_y_trial))

    plt.xlim([-20,20])
    plt.ylim([-20,20])
    ax1.set_aspect('equal', adjustable='box')
    ax2.set_aspect('equal', adjustable='box')
    ax3.set_aspect('equal', adjustable='box')
    plt.show()