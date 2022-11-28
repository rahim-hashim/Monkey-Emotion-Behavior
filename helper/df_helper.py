import time
import pickle
import numpy as np
import pandas as pd
import ipywidgets as widgets
from ipywidgets import interact, IntSlider
from collections import defaultdict
from IPython.display import display

def freeze_headers(df):
  """
  Formats DataFrame for specified HTML style

  Parameters
  ----------
  df : DataFrame
    DataFrame selected for HTML conversion

  Returns
  -------
  df_html : DataFrame
    HTML-converted DataFrame
  """

  df_html = df.to_html() 
  # CSS styling 
  style = """
  <style scoped>
      .dataframe-div {
        max-height: 300px;
        overflow: auto;
        position: relative;
      }

      .dataframe thead th {
        position: -webkit-sticky; /* for Safari */
        position: sticky;
        top: 0;
        background: black;
        color: white;
      }

      .dataframe thead th:first-child {
        left: 0;
        z-index: 1;
      }

      .dataframe tbody tr th:only-of-type {
              vertical-align: middle;
          }

      .dataframe tbody tr th {
        position: -webkit-sticky; /* for Safari */
        position: sticky;
        left: 0;
        background: black;
        color: white;
        vertical-align: top;
      }
  </style>
  """
  # Concatenating to single string
  df_html = style+'<div class="dataframe-div">'+df_html+"\n</div>"
  return(df_html)


def filter_df(dates_selected, remove_uninitiated, blocks_selected, conditions_selected,
            trial_outcome_selected, error_types_selected, save_df, display_df, verbose_df):

  """
  Displays dataframe with selected conditions.
  Updates whenever the widget inputs are updated.

  Parameters
  ----------
  <arg>_selected : <type>
    Specified condition (i.e. blocks, conditions...)
  
  Returns
  -------
  df_working : DataFrame
    DataFrame containing only specified parameters
  """

  # apologies for all the global variables
  # if you've seen the ipywidget, you know it's not my fault...
  global session_df_filtered, dates, blocks, conditions, error_types, save_path
  print('\nTotal number of trials (initiated and uninitiated): {}'.format(len(session_df_filtered.index)))
  correct_ratio_uninitiated_included = np.sum(session_df_filtered['correct'])/len(session_df_filtered['correct'])
  print('\tPerformance: {}%'.format(round(correct_ratio_uninitiated_included*100),4))

  session_df_filtered.sort_values(by=['date', 'session_num'])
  uninitiated_error = 1 ## HARD CODED
  uninitiated_count = len(session_df_filtered[session_df_filtered['error_type'] == uninitiated_error]['correct'])

  if remove_uninitiated:
    # remove all trial errors caused by breaking initial central fixation
    try:
      session_df_filtered_new = session_df_filtered.loc[session_df_filtered['error_type'] != uninitiated_error]
      print('Total number of trials (initiated only): {}'.format(len(session_df_filtered_new.index)))
      correct_ratio_initiated = np.sum(session_df_filtered_new['correct'])/len(session_df_filtered_new['correct'])
      print('\tPerformance: {}%'.format(round(correct_ratio_initiated*100),4))
    except:
      print('Error: check ML trialerror mapping for \'No fixation - center\'')
  else:
    session_df_filtered_new = session_df_filtered
  
  correct_ratio = np.sum(session_df_filtered_new['correct'])/len(session_df_filtered_new['correct'])
  print('\tUninitiated trials count: {}'.format(uninitiated_count))
  print('\t  Uninitiated error code default = {}'.format(uninitiated_error))
  print('\t  (see error_dict and update in df_helper.filter_df\n\t  if mapped differently in your ML code)')

  if dates_selected:
    a = dates_selected
  else:
    a = dates
  if blocks_selected:
    b = blocks_selected
  else:
    b = blocks
  if conditions_selected:
    c = conditions_selected
  else:
    c = conditions
  if trial_outcome_selected == ('Correct',):
    d = (1,)
    error_type = (0,)
  elif trial_outcome_selected == ('Incorrect',):
    d = (0,)
    if error_types_selected:
      error_type = error_types_selected
    else:
      error_type = error_types
  else: # ('Correct', 'Incorrect')
    d = (1,0)
    if error_types_selected:
      error_type = [0] + list(error_types_selected)
    else:
      error_type = [0] + list(error_types)
  print('\nDate(s) Selected: {}'.format(a))
  print('Block(s) Selected: {}'.format(b))
  print('Condition(s) Selected: {}'.format(c))
  print('Trial Outcome Selected: {}'.format(trial_outcome_selected))
  print('Error Type(s) Selected: {}\n'.format(error_type))

  # filter to specific conditions
  session_df_conditional = session_df_filtered_new.loc[(session_df_filtered_new['date'].isin(a)) &\
                                      (session_df_filtered_new['block'].isin(b)) &\
                                      (session_df_filtered_new['condition'].isin(c)) &\
                                      (session_df_filtered_new['correct'].isin(d)) &\
                                      (session_df_filtered_new['error_type'].isin(error_type))]
  session_df_conditional.style.set_properties(**{'color': 'white', 'border-color': 'white'})
  print('Total number of trials (filtered): {}'.format(len(session_df_conditional)))
  correct_ratio = np.sum(session_df_conditional['correct'])/len(session_df_conditional['correct'])
  print('\tPerformance: {}%'.format(round(correct_ratio*100),4))

  if display_df:
    display(session_df_conditional)
    if verbose_df:
      pd.set_option('display.max_rows', None)
    else:
      pd.set_option('display.max_rows', 10)
  if save_df:
    with open(save_path+'session_df_working.pkl', 'wb') as handle:
      t0 = time.time()
      print('Saving session_df_working to: {}'.format(save_path))
      pickle.dump(session_df_conditional, handle, protocol=pickle.HIGHEST_PROTOCOL)
      t1 = time.time()
      total_t = round(t1-t0, 4)
      print('\tTotal time to pickle: {} sec'.format(total_t))
  global session_df_working
  session_df_working = session_df_conditional.copy()

def widgets_df(session_df, error_dict, target_path):
  """
  Generates the widgets for session- and trial-specific parameters

  Parameters
  ----------
  session_df : DataFrame
    Dataframe of all sessions
  error_dict : dict
    Dictionary containing all ML trialerror mappings
  target_path : str
    Path for saving the filtered dataframe

  Returns
  -------
  out: 
    ipywidgets Output() containing all widget information
  """

  global session_df_filtered, dates, blocks, conditions, error_types, filename, save_path

  dates = sorted(session_df['date'].unique())
  blocks = sorted(session_df['block'].unique())
  conditions = sorted(session_df['condition'].unique())
  error_types = sorted(session_df['error_type'].unique())[1:]
  error_words = list(map(lambda x: error_dict[str(x)], error_types))
  eye_distance = defaultdict(list)

  dates_selected = widgets.SelectMultiple(options=dates,
                                          description='Dates')
  blocks_selected = widgets.SelectMultiple(options=blocks,
                                           description='Blocks')
  conditions_selected = widgets.SelectMultiple(options=conditions,
                                               description='Conditions')
  trial_outcome_selected = widgets.SelectMultiple(options=['Correct', 'Incorrect'],
                                                  description='Trial Outcome')
  error_types_selected = widgets.SelectMultiple(options=error_types,
                                                description='Error Type')
  display_df = widgets.Checkbox(value=False, description='Display dataframe')
  verbose_df = widgets.Checkbox(value=False, description='See all dataframe rows')
  remove_uninitiated = widgets.Checkbox(value=True, description='Remove uninitiated trials')
  save_df = widgets.Checkbox(value=True, description='Save working dataframe')
  
  session_df_filtered = session_df.copy()
  save_path = target_path
  out = widgets.interactive_output(filter_df, {
                                     'dates_selected': dates_selected,
                                     'remove_uninitiated': remove_uninitiated,
                                     'blocks_selected': blocks_selected,
                                     'conditions_selected': conditions_selected,
                                     'trial_outcome_selected': trial_outcome_selected,
                                     'error_types_selected': error_types_selected,
                                     'save_df': save_df,
                                     'display_df': display_df,
                                     'verbose_df': verbose_df,
                                     })

  window_description = widgets.VBox([remove_uninitiated,
                                     display_df,
                                     verbose_df,
                                     save_df,
                                     ])

  display(widgets.HBox([widgets.VBox([
                        dates_selected,
                        blocks_selected,
                        conditions_selected,
                        trial_outcome_selected,
                        error_types_selected]),
                        window_description
                        ]))
  return out

def df_summary(df, error_dict):    
  """
  Prints a summary of the sessions parsed

  Parameters
  ----------
  df : DataFrame
    dataframe of all sessions
  error_dict : dict
      dictionary containing all ML trialerror mappings

  Returns
  -------
  Prints:
    1) performance (by block)
    2) performance (by condition)
    3) performance (by trial outcome)
  """


  blocks = sorted(df['block'].unique())
  conditions = sorted(df['condition'].unique())
  error_types = sorted(df['error_type'].unique())[1:]
  error_words = list(map(lambda x: error_dict[str(x)], error_types))

  # by blocks
  for block in blocks:
    correct_in_block = df[df['block']==block]['correct']
    correct_count_block = np.sum(correct_in_block)
    trial_count_block = len(correct_in_block)
    block_correct_ratio = np.round(correct_count_block/trial_count_block, 3)
    print('  Block {} – {} (n={}/{})'.format(block,
                                             block_correct_ratio,
                                             correct_count_block,
                                             trial_count_block))
  # by conditions
  for condition in conditions:
    correct_in_condition = df[df['condition']==condition]['correct']
    correct_count_cond = np.sum(correct_in_condition)
    trial_count_cond = len(correct_in_condition)
    condition_correct_ratio = np.round(correct_count_cond/trial_count_cond, 3)
    print('  Condition {} – {} (n={}/{})'.format(condition, 
                                                 condition_correct_ratio,
                                                 correct_count_cond,
                                                 trial_count_cond))
    error_list = df[df['condition']==condition]['error_type'] # list of all errors in session
    error_types = error_list.unique()
    for error in sorted(error_types[np.nonzero(error_types)]): # errors are non-zero (0 = correct):
      print('    error {} - {}: {}'.format(error,
                                           error_dict[str(error)],
                                           np.count_nonzero(error_list==error)))
  
  # by trial outcomes
  print('\nOutcomes: {}'.format(sorted(error_types)))
  outcome_count = []
  outcome_names = []
  for e_index, error_type in enumerate(sorted(error_types)):
    error_words = str(error_type)
    df_select_error = df[df['error_type']==error_type]
    trials_select_error = df_select_error['eye_x'].index
    print('  Number of trials with trial outcome type {}: {}'.format(error_type, len(trials_select_error)))
    outcome_names.append(error_dict[str(error_type)])
    outcome_count.append(len(trials_select_error))
  return(outcome_names, outcome_count)