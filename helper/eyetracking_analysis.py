import math 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp2d
from matplotlib.image import NonUniformImage
from collections import defaultdict, OrderedDict
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

def calc_dist(x2, x1, y2, y1):
  dist = math.hypot(x2 - x1, y2 - y1)
  return dist

def eye_delay(trial, xy_axis, session_obj):
  eye_window = session_obj.window_blink
  eye_window = 500 # last 200 ms
  delay_end = trial['Trace End']
  eye_axis = 'eye_' + xy_axis
  eye_data = trial[eye_axis][delay_end-eye_window:delay_end]
  pupil = trial['eye_pupil'][delay_end-eye_window:delay_end]
  eye_filtered = eye_data[pupil != 0]
  return eye_data

def print2dhist(H, xedges, yedges, ax2, label):
  defensive_eye_position = 0
  for x in range(len(xedges)-1):
    for y in range(len(yedges)-1):
      x_edge = xedges[x]
      y_edge = yedges[y]
      if label == True:
        color = 'white' if H[x][y] > 0.15 else 'black'
        ax2.text(x_edge+5, y_edge+5, "{:.2f}".format(H[x, y]), 
                ha="center", va="center", size=10, color=color)
      if y == 0:
        print(x_edge, end='   ')
      if abs(x_edge) > 10 or abs(y_edge) > 10:
        defensive_eye_position += H[x][y]
  defensive_eye_percentage = defensive_eye_position*100
  print(end='\n')
  print(np.flip(H, axis=0)) # edges are -40 -> 40 but yaxis is 40 -> -40
  print('outside x,y [-10, 10]: {}%'.format(round(defensive_eye_percentage, 2)))

def eyetracking_analysis(df, session_obj, TRIAL_THRESHOLD):
  df['eye_delay_x'] = df.apply(eye_delay, xy_axis='x', session_obj=session_obj, axis=1)
  df['eye_delay_y'] = df.apply(eye_delay, xy_axis='y', session_obj=session_obj, axis=1)
  df_count = df[df['fractal_count_in_block'] > TRIAL_THRESHOLD]
  axis_min = -40
  axis_max = 40
  xedges = np.linspace(axis_min, axis_max, 9)
  yedges = np.linspace(axis_min, axis_max, 9)
  for v_index, valence in enumerate(sorted(df['valence'].unique(), reverse=True)):
    df_valence = df_count[df_count['valence'] == valence]
    eye_x_delay = df_valence['eye_delay_x'].tolist()
    eye_y_delay = df_valence['eye_delay_y'].tolist()
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(12, 5))
    # Scatter plot
    ax1.scatter(s=1, x=eye_x_delay, y=eye_y_delay, 
                color=session_obj.valence_colors[v_index],
                alpha=0.25)
    ax1.set_xlim(axis_min, axis_max)
    ax1.set_ylim(axis_min, axis_max)
    ax1.grid(True)
    ax1.set_xticks(np.arange(axis_min, axis_max+1, 10))
    ax1.set_title('scatter plot')
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    # 2D histogram
    x_flatten = [item for sublist in eye_x_delay for item in sublist]
    y_flatten = [item for sublist in eye_y_delay for item in sublist]
    print(len(x_flatten))
    H, xedges, yedges = np.histogram2d(x_flatten, y_flatten,
              bins=(xedges, yedges), density=True)
    H_sum = np.sum(H)
    print('H_sum: {}'.format(H_sum))
    H = H/H_sum
    cmap = plt.cm.Reds if valence < 0 else plt.cm.Blues
    with np.printoptions(precision=4, suppress=True):
      print2dhist(H, xedges, yedges, ax2, label=True)
    # Histogram does not follow Cartesian convention (see Notes),
    # therefore transpose H for visualization purposes. 
    H = H.T # see np.histogram2d documentation for details
    # ax2.imshow(H, cmap=cmap, extent=(axis_min, axis_max, axis_min, axis_max), 
    #             interpolation='spline16')
    # vmin,vmax = 0.0,0.35
    vmin,vmax = None,None
    im = ax2.pcolormesh(xedges, yedges, H, vmin=vmin,vmax=vmax, cmap=cmap)
    ax2.set_xlabel('x')
    ax2.set_ylabel('y')
    ax2.set_xticks(np.arange(axis_min, axis_max+1, 10))
    ax2.set_title('histogram')
    ax2.set_facecolor('black')
    ax2.grid()
    fig.tight_layout()
    fig.colorbar(im, ax=ax2)
    plt.show()
    # ax2.imshow(H, cmap=cmap, interpolation = 'nearest')
    # plt.show()