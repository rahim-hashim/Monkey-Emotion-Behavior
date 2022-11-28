import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
from scipy.interpolate import make_interp_spline, BSpline

from plot_helper import smooth_plot, round_up_to_odd, moving_avg

pd.options.mode.chained_assignment = None  # default='warn'

def session_performance(df, behavioral_code_dict, latency, session_obj):

  FIGURE_SAVE_PATH = session_obj.figure_path
  COLORS = session_obj.colors
  LABELS = session_obj.stim_labels

  # All Trials
  trial_num = np.array(range(len(df['trial_num'])))
  correct_list = np.array(df['correct'])

  # Only CS Presented Trials
  cs_on_index = [index for index in behavioral_code_dict.keys() if behavioral_code_dict[index] == 'CS On'][0]
  session_df_CS_presented = df[df['behavioral_code_markers'].apply(lambda x: cs_on_index in x)]

  gs_kw = dict(width_ratios=[6, 1])
  f, (ax1, ax2) = plt.subplots(1, 2, gridspec_kw=gs_kw, figsize=(20,5))
  correct_list_filtered = session_df_CS_presented['correct'].tolist()
  color_list_filtered = []
  dates = list(map(int, df['date']))
  new_dates = np.diff(dates,prepend=dates[0])

  # poly_order = 2
  # correct_moving_average = np.array(df_moving_avg['correct_list_moving_avg'])
  # window_size = round_up_to_odd(int(len(correct_moving_average)/15))
  # y = signal.savgol_filter(correct_moving_average, int(window_size), poly_order)
  num_rolling = 10
  y = moving_avg(correct_list_filtered, num_rolling)
  x = list(range(len(y)))
  
  # random choice threshold
  ax1.axhline(y=0.5, color='lightgrey',linewidth=1)

  # Coloring in fractal 
  for i in range(len(correct_list_filtered)):
    if session_df_CS_presented.iloc[i]['stimuli_name'] == '_fractal_A':
      ax1.axvspan(xmin=i-0.35, xmax=i+0.35, ymin=0.15, ymax=0.85, alpha=0.2, color=COLORS[0])
      color_list_filtered.append(COLORS[0])
    elif session_df_CS_presented.iloc[i]['stimuli_name'] == '_fractal_B':
      ax1.axvspan(xmin=i-0.35, xmax=i+0.35, ymin=0.15, ymax=0.85, alpha=0.2, color=COLORS[1])
      color_list_filtered.append(COLORS[1])
    elif session_df_CS_presented.iloc[i]['stimuli_name'] == '_fractal_C':
      ax1.axvspan(xmin=i-0.35, xmax=i+0.35, ymin=0.15, ymax=0.85, alpha=0.2, color=COLORS[2])
      color_list_filtered.append(COLORS[2])
    elif session_df_CS_presented.iloc[i]['stimuli_name'] == '_fractal_D':
      ax1.axvspan(xmin=i-0.35, xmax=i+0.35, ymin=0.15, ymax=0.85, alpha=0.2, color=COLORS[3])
      color_list_filtered.append(COLORS[3])
    elif session_df_CS_presented.iloc[i]['stimuli_name'] == '_fractal_E':
      ax1.axvspan(xmin=i-0.35, xmax=i+0.35, ymin=0.15, ymax=0.85, alpha=0.2, color=COLORS[4])
      color_list_filtered.append(COLORS[4])

  title_str = 'Performance By Fractal'
  ax1.set_title(label=title_str, ha='center', fontsize=16)

  ax1.plot(x, y, linewidth=4, color='black')
  correct_list_filtered = [r+0.1 if r==1 else r-0.1 for r in correct_list_filtered]
  ax1.scatter(x, correct_list_filtered[num_rolling-1:], s=6, color=color_list_filtered[num_rolling-1:])
  ax1.set_ylim([-0.2,1.2])
  ax1.set_yticks([0,0.5,1])
  ax1.set_xlabel('Trial Number', fontsize=16)
  ax1.set_ylabel('Rolling Average (n={})'.format(num_rolling), fontsize=16)
  date_lines = list(np.nonzero(new_dates)[0])
  for date in date_lines:
    ax1.axvline(x=date, c='lightgrey', linestyle='-')
  f.tight_layout(pad=2)

  rewards = []
  for fractal in session_df_CS_presented['stimuli_name'].unique():
    session_df_fractal = session_df_CS_presented[session_df_CS_presented['stimuli_name'] == fractal]
    reward_val = np.sum(session_df_fractal['correct'])/len(session_df_fractal)
    rewards.append(reward_val)

  x = np.arange(len(rewards))
  ax2.bar(np.arange(len(rewards)), rewards, color=COLORS, ec='black')
  ax2.set_xticks(x) # values
  ax2.set_xticklabels(LABELS) # labels
  ax2.set_xlabel('Fractal')
  ax2.set_ylabel('% Fixation Hold (CS On)')
  ax2.set_ylim([0,1])
  #ax2.set_title('Performance by Fractal')
  
  img_save_path = os.path.join(FIGURE_SAVE_PATH, 'perf_by_fractal')
  print('  perf_by_fractal.png saved.')
  plt.savefig(img_save_path, dpi=150, bbox_inches='tight', pad_inches = 0.1)
  plt.close('all')

#   # latency
#   if (len(df['date'].unique()) == 1) and (latency == True):
#     trial_absolute_start = df['trial_absolute_start']
#     df['latency'] = np.diff(trial_absolute_start, prepend=trial_absolute_start.iloc[0])/1000
#     latency = df['latency'].rolling(5).mean()
#     y = signal.savgol_filter(latency, 31, 5)
#     f, ax = plt.subplots(1, figsize=(20,5))
#     plt.plot(range(len(latency)), y)
#     blocks = list(map(int, df['block']))
#     new_blocks = np.diff(blocks,prepend=blocks[0])
#     block_lines = list(np.nonzero(new_blocks)[0])
#     for block in block_lines:
#       ax.axvline(x=block, c='lightgrey', linestyle='-')
#     title_str = 'Latency ' + title 
#     plt.title(title_str)
#     plt.ylabel('Latency')
#     plt.xlabel('Trial Number')
#     plt.show()

# def perf_by_fractal(session_df, behavioral_code_dict, colors, FIGURE_SAVE_PATH):