import os
import numpy as np
import pandas as pd
from scipy import signal
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib import cm
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

from plot_helper import round_up_to_odd
from Session import Session

def plot_latency(df: pd.DataFrame, session_obj: Session):
  """
  plot_latency plots the trial-by-trial latency for the session

  Args
    df (pd.DataFrame):
      session DataFrame
    session_obj (Session):
      Session object with metadata and plotting parameters

  Plots
    ax1 (plt.subplots):
      smoothened line plot of average trial latency
    ax2 (plt.subplots):
      bar graph of average latency by reward history
  """
  import seaborn as sns
  f, ax = plt.subplots(1,1)
  latency = df['Fixation Success'].tolist()
  valence_1_back = df.shift(1)['valence']
  sns.barplot(x=valence_1_back, y=latency, ax=ax, estimator=np.mean,
              palette=reversed(session_obj.valence_colors), 
              ec='black', 
              lw=1)


def plot_session_timing(df: pd.DataFrame, session_obj: Session):
  """
  plot_session_timing plots the trial-by-trial latency for the session

  Args
    df (pd.DataFrame):
      session DataFrame
    session_obj (Session):
      Session object with metadata and plotting parameters

  Plots
    ax1 (plt.subplots):
      smoothened line plot of average trial latency
    ax2 (plt.subplots):
      bar graph of average latency by reward history
  """

  gs_kw = dict(width_ratios=[4, 1])
  f, (ax1, ax2) = plt.subplots(1,2, gridspec_kw=gs_kw, figsize=(20,3))

  time_diff = np.diff(df['trial_datetime_start'].tolist()) # difference in trial starttimes
  df['latency'] = [0] + [round(float(trial.seconds)+(float(trial.microseconds)/1000000), 2)\
                    for trial in time_diff] # leading zero to capture latency for NEXT trial

  correct = df['correct']
  rewarded_trials = df['reward'] * correct
  rewarded_trials = [r+0.1 if r==1 else r-0.1 for r in rewarded_trials]

  time_per_trial = df['latency'].tolist()
  session_median = np.median(time_per_trial)
  session_std = np.std(time_per_trial)
  outliers_removed = [trial if trial < (session_median + 10*session_median) else session_median \
                      for trial in time_per_trial]
  outliers = (set(time_per_trial) ^ set(outliers_removed))
  outlier_indices = [time_per_trial.index(outlier) for outlier in outliers if outlier != session_median]
  ax1.axhline(session_median, color='red', alpha=0.4)
  for outlier in outlier_indices:
    ax1.axvline(outlier, color='grey', alpha=0.4)
  # smoothening latency plot
  poly_order = 4
  x = np.arange(len(outliers_removed))
  window_size = round_up_to_odd(int(len(np.array(outliers_removed))/15))
  y = signal.savgol_filter(outliers_removed, int(window_size), poly_order)
  ax1.plot(x, y, linewidth=3)
  ax1.text(len(x) + 5, session_median+1, s='median', color='red', alpha=0.4, fontsize=8)

  color_list = ['limegreen' if trial else 'red' for trial in correct] # green if correct and rewarded, else red
  ax1b = ax1.twinx()
  ax1b.scatter(np.arange(len(rewarded_trials)), rewarded_trials, s=4, color=color_list)
  ax1b.set_yticks([-0.1, 1.1], ['no reward', 'reward'])
  ax1.set_xlabel('Trial Number')
  ax1.set_ylabel('Latency (s)')

  correct_patch = mpatches.Patch(color='limegreen', label='Correct')
  incorrect_patch = mpatches.Patch(color='red', label='Incorrect')
  ax1.legend(handles=[correct_patch, incorrect_patch], loc='center left', prop={'size': 6})

  one_back_noreward = df[df['reward_1_back'] == 0]
  one_back_reward = df[df['reward_1_back'] == 1]  
  two_back_noreward = df[df['reward_2_back'] == 0]
  two_back_reward = df[df['reward_2_back'] == 2] 
  three_back_noreward = df[df['reward_3_back'] == 0]
  three_back_reward = df[df['reward_3_back'] == 3]
  four_back_noreward = df[df['reward_4_back'] == 0]
  four_back_reward = df[df['reward_4_back'] == 3]
  five_back_noreward = df[df['reward_5_back'] == 0]
  five_back_reward = df[df['reward_5_back'] == 4]

  latency_five_norewards = np.mean(five_back_noreward['latency'])
  latency_four_norewards = np.mean(four_back_noreward['latency'])
  latency_three_norewards = np.mean(three_back_noreward['latency'])
  latency_two_norewards = np.mean(two_back_noreward['latency'])
  latency_one_noreward = np.mean(one_back_noreward['latency'])
  latency_one_reward = np.mean(one_back_reward['latency'])
  latency_two_rewards = np.mean(two_back_reward['latency'])
  latency_three_rewards = np.mean(three_back_reward['latency'])
  latency_four_rewards = np.mean(four_back_reward['latency'])
  latency_five_rewards = np.mean(five_back_reward['latency'])

  latency_list = [latency_five_norewards, latency_four_norewards, latency_three_norewards, latency_two_norewards, latency_one_noreward,
                  latency_one_reward, latency_two_rewards, latency_three_rewards, latency_four_rewards, latency_five_rewards]
  
  # color by value
  my_cmap = plt.get_cmap('RdYlGn')
  rescale = lambda latency_list: (latency_list - np.min(latency_list)) / (np.max(latency_list) - np.min(latency_list))
  
  # color by order
  clist = [(0, 'red'), (1, 'limegreen')]
  rvb = mcolors.LinearSegmentedColormap.from_list("", clist)
  N = len(latency_list)
  x = np.arange(len(latency_list))
  ax2.bar(x, latency_list, color=rvb(x/N), ec='black')
  xlabels = ['-5', '-4', '-3', '-2', '-1', '+1', '+2', '+3', '+4', '+5']
  ax2.tick_params(axis='y', which='major', labelsize=8)
  ax2.set_xticks(np.arange(len(xlabels)), xlabels)
  ax2.set_xlabel('Consecutive Rewards (+) / Omissions (-)')
  ax2.set_ylabel('Avg Latency (s)')

  plt.tight_layout()

  FIGURE_SAVE_PATH = session_obj.figure_path  
  img_save_path = os.path.join(FIGURE_SAVE_PATH, 'session_latency')

  plt.savefig(img_save_path, dpi=150, bbox_inches='tight', pad_inches = 0.1)
  print('  session_latency.png saved.')

  plt.close()