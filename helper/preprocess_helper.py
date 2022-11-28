import os
import sys
import pandas as pd
from pprint import pprint
import h5_helper

def preprocess_data(h5_filenames, path_obj, start_date, end_date, monkey_input, reprocess_data, save_df):
  current_path = path_obj.CURRENT_PATH
  target_path = path_obj.TARGET_PATH
  # preprocess data
  if reprocess_data:
    ml_config, trial_record, session_df, error_dict, behavioral_code_dict = \
      h5_helper.h5_to_df(current_path, target_path, h5_filenames, start_date, end_date, monkey_input, save_df)
    return ml_config, trial_record, session_df, error_dict, behavioral_code_dict
  # pickle preprocessed data
  else:
    print('\nFiles uploaded from processed folder\n')
    all_selected_dates = h5_helper.date_selector(start_date, end_date)
    target_dir = os.listdir(target_path)
    pkl_files_selected, dates_array = h5_helper.file_selector(target_dir, all_selected_dates, monkey_input)
    print('Pickled Files:')
    pprint(pkl_files_selected)
    for f_index, f in enumerate(pkl_files_selected):
      target_pickle = os.path.join(target_path, f)
      if os.path.exists(target_pickle):
        session_dict = pd.read_pickle(target_pickle)
        if f_index == 0:
          session_df = session_dict['data_frame']
          error_dict = session_dict['error_dict']
          behavioral_code_dict = session_dict['behavioral_code_dict']
        else:
          session_df_new = session_dict['data_frame']
          session_df = session_df.append(session_df_new, ignore_index=True)
          error_dict = session_dict['error_dict']
          behavioral_code_dict = session_dict['behavioral_code_dict']    
      else:
        print('\nPickled files missing. Reprocess or check data.')
        sys.exit()
    return None, None, session_df, error_dict, behavioral_code_dict