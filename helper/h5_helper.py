import os
import sys
import h5py
import time
import pickle
import pandas as pd
import ipywidgets as widgets
from datetime import date, timedelta
from collections import defaultdict
from IPython.display import display

from session_parse_helper import session_parser

def h5_pull(current_dir):
  """Look for all .h5 extension files in directory"""
  print('Pulling \'.h5\' files...')
  h5_filenames = [f for f in current_dir if f[-3:] == '.h5']
  print('Complete: {} \'.h5\' files pulled'.format(len(h5_filenames)))
  return h5_filenames

def h5_load(file_name):
  """Loads h5 datasets into a python object"""
  f = h5py.File(file_name, 'r')
  return f

def h5_parse(f):
  """Parses out groups and subgroups from .h5 tree

  Args:
    .h5 file (tree configuration below):
      - group: 'ML'
      - subgroup: 
        - 'MLConfig'
        - 'TrialResults'
        - 'Trialn'

  Returns:
    Each subgroup (listed in Args) as a unique variable
  """
  trial_list = []
  for group in list(f.keys()):
    for subgroup in list(f[group].keys()):
      try:
        trial_num = int(subgroup[5:]) # trials all end in numbers (i.e. Trial1, Trial2,...Trialn)
        trial_list.append(subgroup)
      except:
          pass
  print('  Total number of trials: {}'.format(len(trial_list)))
  ml_config = f['ML']['MLConfig']
  trial_record = f['ML']['TrialRecord']
  return ml_config, trial_record, trial_list

def config_viewer(ml_config):
  """widget manager"""
  w = widgets.Dropdown(
    options=ml_config.keys(),
    description='ml_config parameter:',
  )

  def on_change(change):
    if change['type'] == 'change' and change['name'] == 'value':
      param = change['new']
      try:
        print('{}: {}'.format(param, str(ml_config[param][...])))
      except TypeError:
        print('Value: {}'.format(param, list(ml_config[param])))
      except AttributeError:
        print('Value: {}'.format(param, list(val.encode('utf-8') for val in ml_config[param])))            
      except TypeError:
        pass
        print('Value: {}\n'.format(param, str(ml_config[param])))

  w.observe(on_change)
  display(w)

def trial_record_viewer(trial_record):
  w = widgets.Dropdown(
    options=trial_record.keys(),
    description='trial_record parameter:',
  )

  def on_change(change):
    if change['type'] == 'change' and change['name'] == 'value':
      param = change['new']
      try:
        print('{}: {}'.format(param, list(trial_record[param])))
      except TypeError:
        print('{}: {}'.format(param, str(trial_record[param])))

  w.observe(on_change)
  display(w)

def pickler(save_df, save_path, session_df, monkey_input, experiment_name,
            error_dict, behavioral_code_dict):
  """Pickles each session (by date)"""
  if save_df:
    session_dict = {}
    print('Saving .pickle files to: {}'.format(save_path))
    all_dates = session_df['date'].unique()
    for date in all_dates:
      date_df = session_df[session_df['date']==date]
      file_name = '_'.join([date,monkey_input,experiment_name,'behave.pkl'])
      if os.path.exists(save_path) == False:
        os.mkdir(save_path)
      file_path_save = os.path.join(save_path, file_name)
      with open(file_path_save, 'wb') as handle:
        t0 = time.time()
        print('  Pickling {}'.format(file_name))
        session_dict['data_frame'] = date_df
        session_dict['error_dict'] = error_dict
        session_dict['behavioral_code_dict'] = behavioral_code_dict
        pickle.dump(session_dict, handle, protocol=4) # google colab only supports protocol 4
        t1 = time.time()
        total_t = round(t1-t0, 4)
        print('    Total time to pickle: {} sec'.format(total_t))

def date_selector(start_date, end_date):
  """Selects dates from colab forms input"""
  all_selected_dates = [] # array containing all dates
  start_y = start_date[:4]; start_m = start_date[5:7]; start_d = start_date[8:]
  end_y = end_date[:4]; end_m = end_date[5:7]; end_d = end_date[8:]
  d1 = date(int(start_y), int(start_m), int(start_d))
  d2 = date(int(end_y), int(end_m), int(end_d))
  dates_between = [d1 + timedelta(days=x) for x in range((d2-d1).days + 1)]
  for date_between in dates_between:
    year = str(date_between.year)
    month = f"{date_between:%m}"
    day = f"{date_between:%d}"
    date_formatted = year[2:4]+month+day
    all_selected_dates.append(date_formatted)
  return all_selected_dates

def file_selector(file_dir, all_selected_dates, monkey_input):
    """
    file_selector checks selected dates from date_selector
    and returns the appropriate files from file_dir
    """
    files_selected = []
    dates_array = []
    for f in file_dir:
      for date_formatted in all_selected_dates:
        if (date_formatted in f) and (monkey_input in f):
          files_selected.append(f)
          dates_array.append(date_formatted)
    return files_selected, dates_array

def h5_to_df(current_path, target_path, h5_filenames, start_date, end_date, monkey_input, save_df):
  """Converts specified (by date) .h5 files to DataFrame and pickles 

  Args:
    current_path: 
      root+datapath (specified in monkey_behavior.ipynb)
    h5_filenames: 
      names of all the pulled .h5 files
    start_date: 
      first date pulled (specified in monkey_behavior.ipynb)
    end_date: 
      last date pulled (specified in monkey_behavior.ipynb)
    monkey_input: 
      name of monkey (specified in monkey_behavior.ipynb)
    save_df: 
      boolean specifying whether or not to pickle resulting DataFrames (specified in monkey_behavior.ipynb)

  Returns:
    ml_config:
      .h5 group containing MonkeyLogic configuration parameters
    trial_record:
      .h5 group containing MonkeyLogic trial_record
    session_df:
      DataFrame containing all sessions captured
    error_dict:
      dictionary containing error mapping
  """
  all_selected_dates = date_selector(start_date, end_date)
  h5_files_selected, dates_array = file_selector(h5_filenames, all_selected_dates, monkey_input)
  python_converted_files = []
  if h5_files_selected:
    print('Loading selected file(s):')
    for f in h5_files_selected:
      file_name = os.path.join(current_path, f)
      if os.path.exists(file_name):
        python_converted_files.append(h5_load(file_name))
        print('  {} - Completed'.format(f))
      else:
        print('  {} - Missing'.format(f))
  else:
    print('All files:')
    for f in h5_filenames:
      print(' ', f)
      raise RuntimeError('No file found - check directory')

  print('Converting .h5 to python:')
  if python_converted_files:
    for f_index, f in enumerate(python_converted_files):
      print('  {}'.format(f))
      ml_config, trial_record, trial_list = h5_parse(f)
      session_dict, error_dict, behavioral_code_dict = \
        session_parser(f, trial_list, trial_record, dates_array[f_index], monkey_input)
      if f_index == 0:
        session_df = pd.DataFrame.from_dict(session_dict) # convert dictionary to pd.DataFrame
      else:
        session_df_new = pd.DataFrame.from_dict(session_dict)
        session_df = session_df.append(session_df_new, ignore_index=True)
    experiment_name = ml_config['ExperimentName'][...].tolist().decode()

    pickler(save_df, target_path, session_df, monkey_input, experiment_name,
            error_dict, behavioral_code_dict) # pickles individual session
  else:
      raise RuntimeError('No .h5 files found for selected dates')

  return ml_config, trial_record, session_df, error_dict, behavioral_code_dict