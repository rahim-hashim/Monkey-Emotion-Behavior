import os
import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt
from collections import defaultdict

from Session import Session
from plot_helper import smooth_plot, round_up_to_odd, moving_avg

def session_lick(df: pd.DataFrame, session_obj: Session):
  '''
    session_lick plots the lick duration within the last <session_obj.window>ms of delay 
    across the entire session broken down by fractal

    Args
      - df (pd.DataFrame): session DataFrame
      - session_obj (Session): Session object with metadata and plotting parameters

    Plots
      - axarr1 (plt.subplots): smoothened line plot of average lick trace each trial
        across session
      - axarr2 (plt.subplots): smoothened line plot of blink count each trial
        across session
  '''
  
  LABELS = session_obj.stim_labels
  COLORS = session_obj.colors
  FIGURE_SAVE_PATH = session_obj.figure_path
  LICK_WINDOW_THRESHOLD = session_obj.window_lick
  BLINK_WINDOW_THRESHOLD = session_obj.window_blink

  f1, axarr1 = plt.subplots(len(LABELS),1, sharex=True, sharey=True, figsize=(10,5))
  f2, axarr2 = plt.subplots(len(LABELS),1, sharex=True, sharey=True, figsize=(10,5))

  for df_index, fractal in enumerate(sorted(df['stimuli_name'].unique())):

    df_fractal = df[df['stimuli_name'] == fractal]

    df_fractal['block_change'] = df_fractal['block'].diff()
    block_change = np.nonzero(df_fractal['block_change'].tolist())[0]

    # Lick / Reward Plot
    lick = df_fractal['lick_in_window']
    lick = [r+0.1 if r==1 else r-0.1 for r in lick]

    lick_raster_window = df_fractal['lick_count_window'].tolist()
    lick_raster_window = list(map(np.mean, lick_raster_window))
    x1 = np.arange(len(lick_raster_window))
    window_size = round_up_to_odd(int(len(np.array(lick_raster_window))/15))
    poly_order = 3
    y1 = signal.savgol_filter(lick_raster_window, int(window_size), poly_order)
    axarr1[df_index].plot(np.array(x1), y1, linewidth=3, label = LABELS[df_index], color=COLORS[df_index])
    axarr1[df_index].scatter(np.array(x1), lick, s=4, color=COLORS[df_index])

    axarr1[df_index].set_title('Fractal {}'.format(LABELS[df_index], fontsize=12))

    for change_trial in block_change[1:]:
      axarr1[df_index].axvline(change_trial, c='grey', alpha=0.5)

    # Blink Plot
    blink = df_fractal['blink_in_window']
    blink = [a+0.1 if a==1 else a-0.1 for a in blink]

    blink_raster_window = df_fractal['blink_in_window'].tolist()
    x2 = np.arange(len(blink_raster_window))
    window_size = round_up_to_odd(int(len(np.array(blink_raster_window))/15))
    y2 = signal.savgol_filter(blink_raster_window, int(window_size), poly_order)
    axarr2[df_index].plot(np.array(x2), y2, linewidth=3, label = LABELS[df_index], color=COLORS[df_index])
    axarr2[df_index].scatter(np.array(x2), blink, s=4, color=COLORS[df_index])

    axarr2[df_index].set_title('Fractal {}'.format(LABELS[df_index], fontsize=8))

    for change_trial in block_change[1:]:
      axarr2[df_index].axvline(change_trial, c='grey', alpha=0.5)

  f1.supylabel('Lick Trace Avg\n(Last {}ms of Delay)'.format(LICK_WINDOW_THRESHOLD))
  axarr1[0].set_xlabel('Trial Count')
  axarr1[0].set_ylim([-0.15, 1.15])
  axarr1[0].set_yticks([-0.15, 0, 1, 1.15])
  axarr1[0].set_yticklabels(['', '0', '1', ''])
  f1.tight_layout()
  img_save_path = os.path.join(FIGURE_SAVE_PATH, 'session_lick_avg')
  f1.savefig(img_save_path, dpi=150, bbox_inches='tight', pad_inches = 0.1)
  print('  session_lick_avg.png saved.')

  f2.supylabel('Probability of Blink\n(Last {}ms of Delay)'.format(BLINK_WINDOW_THRESHOLD))
  axarr2[0].set_xlabel('Trial Count')
  axarr2[0].set_ylim([-0.15, 1.15])
  axarr2[0].set_yticks([-0.15, 0, 1, 1.15])
  axarr2[0].set_yticklabels(['', '0', '1', ''])
  f2.tight_layout()
  img_save_path = os.path.join(FIGURE_SAVE_PATH, 'session_blink_avg')
  f2.savefig(img_save_path, dpi=150, bbox_inches='tight', pad_inches = 0.1)
  print('  session_blink_avg.png saved.')
