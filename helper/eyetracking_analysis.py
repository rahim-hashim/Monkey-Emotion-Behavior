import math 
import numpy as np
import pandas as pd
import matplotlib.colors
from operator import itemgetter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import defaultdict, OrderedDict

def calc_dist(x2, x1, y2, y1):
  dist = math.hypot(x2 - x1, y2 - y1)
  return dist

def find_eye_target_end(times, codes, eye_x, eye_y):

  eye_data = defaultdict(lambda:defaultdict(list))

  trial_start = codes[1].index(100) # trial start time

  # int() captures the floor of the floating point time value
  trial_start_time = int(times[1][trial_start])
  last_event_code = 100 # for error trials

  # Start -> Fixation on
  try:
    start_fixation_time_index = codes[1].index(101)
    start_fix_on_time = int(times[1][start_fixation_time_index])
    sample_circle_time_normalized = start_fix_on_time - trial_start_time
    eye_x_start_fix = eye_x[1][trial_start_time:start_fix_on_time]
    eye_y_start_fix = eye_y[1][trial_start_time:start_fix_on_time]
    last_event_code = 101
  except: # error code
    eye_x_start_fix = []
    eye_y_start_fix = []
  eye_data['eye_start_fix'] = list(zip(eye_x_start_fix, eye_y_start_fix))

  # Fixation on -> Sample Circle on
  try:
    sample_circle_time_index = codes[1].index(102)
    sample_circle_time = int(times[1][sample_circle_time_index])
    fix_sample_circle_time_normalized = sample_circle_time - trial_start_time
    eye_x_fix_sample_circle = eye_x[1][start_fix_on_time:sample_circle_time]
    eye_y_fix_sample_circle = eye_y[1][start_fix_on_time:sample_circle_time]
    last_event_code = 102
  except: # error code
    eye_x_fix_sample_circle = []
    eye_y_fix_sample_circle = []
  eye_data['eye_fix_sample'] = list(zip(eye_x_fix_sample_circle, eye_y_fix_sample_circle))
  
  # Sample Circle on -> Origin on
  try:
    origin_on_time_index = codes[1].index(103)
    origin_on_time = int(times[1][origin_on_time_index])
    origin_time_normalized = origin_on_time - trial_start_time
    eye_x_sample_origin = eye_x[1][sample_circle_time:origin_on_time]
    eye_y_sample_origin = eye_y[1][sample_circle_time:origin_on_time]
    last_event_code = 103
  except: # error code
    eye_x_sample_origin = []
    eye_y_sample_origin = []
  eye_data['eye_sample_origin'] = list(zip(eye_x_sample_origin, eye_y_sample_origin))
  
  # Origin on -> Sample on 
  try:
    sample_on_time_index = codes[1].index(104)
    sample_on_time = int(times[1][sample_on_time_index])
    sample_time_normalized = sample_on_time - trial_start_time
    eye_x_origin_sample = eye_x[1][origin_on_time:sample_on_time]
    eye_y_origin_sample = eye_y[1][origin_on_time:sample_on_time]
    last_event_code = 104
  except: # error code
    eye_x_origin_sample = []
    eye_y_origin_sample = []
  eye_data['eye_origin_sample'] = list(zip(eye_x_origin_sample, eye_y_origin_sample))

  # Sample on -> Delay
  try:
    delay_time_index = codes[1].index(105)
    delay_time = int(times[1][delay_time_index])
    delay_time_normalized = delay_time - trial_start_time
    eye_x_sample_delay = eye_x[1][sample_on_time:delay_time]
    eye_y_sample_delay = eye_y[1][sample_on_time:delay_time]
    last_event_code = 105
  except: # error code
    eye_x_sample_delay = []
    eye_y_sample_delay = []
  eye_data['eye_sample_delay'] = list(zip(eye_x_sample_delay, eye_y_sample_delay))

  # Delay -> Target Circle on 
  try:
    target_circle_on_time_index = codes[1].index(106)
    target_circle_on_time = int(times[1][target_circle_on_time_index])
    target_circle_time_normalized = target_circle_on_time - trial_start_time
    eye_x_delay_targetcircle = eye_x[1][delay_time:target_circle_on_time]
    eye_y_delay_targetcircle = eye_y[1][delay_time:target_circle_on_time]
    last_event_code = 106
  except: # error code
    eye_x_delay_targetcircle = []
    eye_y_delay_targetcircle = []
  eye_data['eye_delay_targetcircle'] = list(zip(eye_x_delay_targetcircle, eye_y_delay_targetcircle))
  
  # Target Circle on -> Target on
  try:
    target_on_time_index = codes[1].index(107)
    target_on_time = int(times[1][target_on_time_index])
    target_time_normalized = target_on_time - trial_start_time
    eye_x_targetcircle_target = eye_x[1][target_circle_on_time:target_on_time]
    eye_y_targetcircle_target = eye_y[1][target_circle_on_time:target_on_time]
    last_event_code = 107
  except: # error code
    eye_x_targetcircle_target = []
    eye_y_targetcircle_target = []
  eye_data['eye_targetcircle_target'] = list(zip(eye_x_targetcircle_target, eye_y_targetcircle_target))
  
  trial_end_index = codes[1].index(110) # trial ends
  trial_end_time = int(times[1][trial_end_index])
  trial_end_time_normalized = trial_end_time - trial_start_time
  try:
    eye_x_target_end = eye_x[1][target_on_time:trial_end_time]
    eye_y_target_end = eye_y[1][target_on_time:trial_end_time]
    last_event_code = 110
  except: # error code
    eye_x_target_end = []
    eye_y_target_end = []
  eye_data['eye_target_end'] = list(zip(eye_x_target_end, eye_y_target_end))

  if last_event_code != 110:
    last_event_code_index = codes[1].index(last_event_code)
    last_event_code_time = int(times[1][last_event_code_index])
    last_event_code_normalized = last_event_code_time - trial_start_time
    try:
      eye_x_error_end = eye_x[1][last_event_code_time:trial_end_time]
      eye_y_error_end = eye_y[1][last_event_code_time:trial_end_time]
    except: # got to error 9
      eye_x_error_end = []
      eye_y_error_end = []
  eye_data['eye_error_end'] = list(zip(eye_x_error_end, eye_y_error_end))

  return eye_data

def parse_eye_data(df):
  '''Plots eye-tracking data

  Args:
    df:
      DataFrame with specified trial data
    trials_select_error
      trial indices for specified error_type
  
  Returns:
    trials_select_error: 
      dictionary containing all specified session data
  '''
  print('Parsing stimuli target_end, eye target_end, and behavioral cues.')
  # parsing eye data
  eye_data = list(map(find_eye_target_end, 
                        list(df['behavioral_code_times'].iteritems()),
                        list(df['behavioral_code_markers'].iteritems()),
                        list(df['eye_x'].iteritems()),
                        list(df['eye_y'].iteritems())))
  
  return eye_data

def plot_eyes_target(row, eye_data, error_dict):#, sample_circle_times):
  for t_index, trial in enumerate(eye_data):

    trial_num = row['trial_num'].iloc[t_index]
    correct = row['correct'].iloc[t_index]
    condition = row['condition'].iloc[t_index]
    error_type = row['error_type'].iloc[t_index]

    # correct origin, sample, target, distractor target_end
    origin_1_x_pos = row['origin_1_x'].iloc[t_index]; origin_1_y_pos = row['origin_1_y'].iloc[t_index]
    sample_1_x_pos = row['sample_1_x'].iloc[t_index]; sample_1_y_pos = row['sample_1_y'].iloc[t_index]
    origin_2_x_pos = row['origin_2_x'].iloc[t_index]; origin_2_y_pos = row['origin_2_y'].iloc[t_index]
    sample_2_x_pos = row['sample_2_x'].iloc[t_index]; sample_2_y_pos = row['sample_2_y'].iloc[t_index]
    target_x_pos = row['target_x'].iloc[t_index]; target_y_pos = row['target_y'].iloc[t_index]
    distractor_x_pos = row['distractor_x'].iloc[t_index]; distractor_y_pos = row['distractor_y'].iloc[t_index]

    stim_size = 15
    # Making Plots
    fig = make_subplots(rows=1, cols=3, column_widths=[0.2, 0.2, 0.2], 
                        subplot_titles=('Sample Presentation', 'Delay', 'Target Presentation'))

    # Plotting Stimuli
    fig.add_scatter(
      x=[origin_1_x_pos], y=[origin_1_y_pos], mode='markers', text='origin 1',
      marker=dict(size=stim_size, color='black'),
      row=1, col=1, line_color='black', opacity=0.25)
    
    fig.add_scatter(
      x=[sample_1_x_pos], y=[sample_1_y_pos], mode='markers', text='sample',
      marker=dict(size=stim_size, color='cyan'),
      row=1, col=1, line_color='cyan', opacity=0.25)
    
    fig.add_scatter(
      x=[0], y=[0], mode='markers', text='fixation',
      marker=dict(size=stim_size, color='grey'),
      row=1, col=2, line_color='grey', opacity=0.1)    

    fig.add_scatter(
      x=[origin_2_x_pos], y=[origin_2_y_pos], mode='markers', text='origin 2',
      marker=dict(size=stim_size, color='black'),
      row=1, col=3, line_color='black', opacity=0.25)

    fig.add_scatter(
      x=[target_x_pos], y=[target_y_pos], mode='markers', text='target',
      marker=dict(size=stim_size, color='magenta'),
      row=1, col=3, line_color='magenta', opacity=0.75)
    
    fig.add_scatter(
      x=[distractor_x_pos], y=[distractor_y_pos], mode='markers', text='distractor',
      marker=dict(size=stim_size, color='magenta'),
      row=1, col=3, line_color='magenta', opacity=0.25)

    # Add eye fix_sample
    eye_trial = eye_data[t_index]['eye_start_fix']
    if eye_trial:
      eye_x_trial = list(list(zip(*eye_trial))[0])
      eye_y_trial = list(list(zip(*eye_trial))[1])
      #fig.add_trace(go.Scattergl(x=eye_x_trial, y=eye_y_trial, text='Fixation On', line=dict(color="#1053fe")),
      #            row=1, col=1)

    # Add eye fix_sample
    eye_trial = eye_data[t_index]['eye_fix_sample']
    if eye_trial:
      eye_x_trial = list(list(zip(*eye_trial))[0])
      eye_y_trial = list(list(zip(*eye_trial))[1])
      fig.add_trace(go.Scattergl(x=eye_x_trial, y=eye_y_trial, text='Sample Circle On', line=dict(color="#0054fe")),
                  row=1, col=1)
    
    # Add eye sample_circle_origin_on
    eye_trial = eye_data[t_index]['eye_sample_origin']
    if eye_trial:
      eye_x_trial = list(list(zip(*eye_trial))[0])
      eye_y_trial = list(list(zip(*eye_trial))[1])
      fig.add_trace(go.Scattergl(x=eye_x_trial, y=eye_y_trial, text='Origin On', line=dict(color="#0000ff")),
                    row=1, col=1)
      
    # Add eye origin_sample
    eye_trial = eye_data[t_index]['eye_origin_sample']
    if eye_trial:
      eye_x_trial = list(list(zip(*eye_trial))[0])
      eye_y_trial = list(list(zip(*eye_trial))[1])
      fig.add_trace(go.Scattergl(x=eye_x_trial, y=eye_y_trial, text='Sample On', line=dict(color="#ffe476")),
                    row=1, col=1)
      
    # Add eye sample_delay
    eye_trial = eye_data[t_index]['eye_sample_delay']
    if eye_trial:
      eye_x_trial = list(list(zip(*eye_trial))[0])
      eye_y_trial = list(list(zip(*eye_trial))[1])
      fig.add_trace(go.Scattergl(x=eye_x_trial, y=eye_y_trial, text='Delay', line=dict(color="#e5e7e9")),
                    row=1, col=2)

    # Add eye targetcircle_target
    eye_trial = eye_data[t_index]['eye_delay_targetcircle']
    if eye_trial:
      eye_x_trial = list(list(zip(*eye_trial))[0])
      eye_y_trial = list(list(zip(*eye_trial))[1])
      fig.add_trace(go.Scattergl(x=eye_x_trial, y=eye_y_trial, text='Target Circle', line=dict(color="honeydew")),
                    row=1, col=3)

    # Add eye targetcircle_target
    eye_trial = eye_data[t_index]['eye_targetcircle_target']
    if eye_trial:
      eye_x_trial = list(list(zip(*eye_trial))[0])
      eye_y_trial = list(list(zip(*eye_trial))[1])
      fig.add_trace(go.Scattergl(x=eye_x_trial, y=eye_y_trial, text='Target', line=dict(color="#e5e1e7")),
                    row=1, col=3)

    # Add eye target_end
    eye_trial = eye_data[t_index]['eye_target_end']
    if eye_trial:
      eye_x_trial = list(list(zip(*eye_trial))[0])
      eye_y_trial = list(list(zip(*eye_trial))[1])
      fig.add_trace(go.Scattergl(x=eye_x_trial, y=eye_y_trial, text='Choice', line=dict(color="#ff5733")),
                    row=1, col=3)
      
    # Add eye error_end
    eye_trial = eye_data[t_index]['eye_error_end']
    if eye_trial:
      eye_x_trial = list(list(zip(*eye_trial))[0])
      eye_y_trial = list(list(zip(*eye_trial))[1])
      fig.add_trace(go.Scattergl(x=eye_x_trial, y=eye_y_trial, text='Error Trace', line=dict(color="red")),
                    row=1, col=1)

    fig.update_xaxes(range=[-20, 20], row=1, col=1, gridcolor='lightgrey', zerolinewidth=1.5, zerolinecolor='grey')
    fig.update_yaxes(range=[-20, 20], row=1, col=1, gridcolor='lightgrey', zerolinewidth=1.5, zerolinecolor='grey')
    fig.update_xaxes(range=[-20, 20], row=1, col=2, gridcolor='lightgrey', zerolinewidth=1.5, zerolinecolor='grey')
    fig.update_yaxes(range=[-20, 20], row=1, col=2, gridcolor='lightgrey', zerolinewidth=1.5, zerolinecolor='grey')
    fig.update_xaxes(range=[-20, 20], row=1, col=3, gridcolor='lightgrey', zerolinewidth=1.5, zerolinecolor='grey')
    fig.update_yaxes(range=[-20, 20], row=1, col=3, gridcolor='lightgrey', zerolinewidth=1.5, zerolinecolor='grey')
    if error_type == 0:
      error_str = 'Correct'
    else:
      error_str = error_dict[str(error_type)]
    fig.update_layout(showlegend=False, plot_bgcolor = '#fdf6ec', paper_bgcolor='#fdf6ec',
        title_text='Trial {}, Condition {}, Outcome: {} ({})'.format(trial_num, condition, error_type, error_str)
    )
    config = {'displayModeBar': True}
    fig.show(config=config)