import os
import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt

def duration_hist_plot(cs_duration_hist, trace_duration_hist, trial_duration_hist, FIGURE_SAVE_PATH):
  num_bins = 20
  f, (ax1, ax2, ax3) = plt.subplots(1,3, sharey = True, figsize=(10,5))
  
  ax1.hist(cs_duration_hist,
           num_bins, 
           color ='blue',
           alpha = 0.7, 
           ec = 'black')
  ax1.set_xlabel('CS Interval')
  ax1.set_ylabel('Trial Count')

  ax2.hist(trace_duration_hist,
          num_bins, 
          color ='red',
          alpha = 0.7, 
          ec = 'black')
  ax2.set_xlabel('Delay')

  ax3.hist(trial_duration_hist,
           num_bins, 
           color ='purple',
           alpha = 0.7, 
           ec = 'black')
        
  ax3.set_xlabel('Trial End - CS On')
    
  ax2.set_title('Trial Duration',
            fontweight = 'bold')
  
  img_save_path = os.path.join(FIGURE_SAVE_PATH, '_duration_hist')
  print('  duration_hist.png saved.')
  plt.savefig(img_save_path, dpi=150, bbox_inches='tight',pad_inches = 0.1)

def duration_hist(df, behavioral_code_dict, FIGURE_SAVE_PATH):
    
  cs_duration_hist = np.array(df['CS Off'].tolist()) - np.array(df['CS On'].tolist())
  trace_duration_hist = np.array(df['Trace End'].tolist()) - np.array(df['Trace Start'].tolist())
  trial_duration_hist = np.array(df['Trace End'].tolist()) - np.array(df['CS On'].tolist())

  duration_hist_plot(cs_duration_hist, trace_duration_hist, trial_duration_hist, FIGURE_SAVE_PATH)