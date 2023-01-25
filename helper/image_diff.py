import os
import sys
import math
import cv2 as cv
import numpy as np
from PIL import Image, ImageStat
import matplotlib.pyplot as plt
from collections import defaultdict

def save_fractal_images(session_df, TASK_PATH, TRACKER_PATH):
  pass

def calculate_brightness(img_list):
  """
  calculate_brightness calculates the
  average brightness of a list of images
  """
  image_brightness = []
  for image in img_list:
    im = Image.open(image)
    im_RBG = im.convert('RGB')
    stat = ImageStat.Stat(im_RBG)
    r,g,b = stat.rms
    image_brightness.append(math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2)))
  return image_brightness

def image_diff(session_df, session_obj, path_obj, combine_dates):
  """
  image_diff calculates the difference
  between two images
  """
  TASK_PATH = path_obj.TASK_PATH
  TRACKER_PATH = path_obj.TRACKER_PATH
  dates = session_df['date'].unique()
  dates_formatted = []
  for date in dates:
    date_formatted = '20' + date
    dates_formatted.append(date_formatted)
    FRACTAL_PATH = os.path.join(TASK_PATH, '_fractals', date_formatted)
    COLOR_LIST = session_obj.colors

    img_list = sorted([os.path.join(FRACTAL_PATH, img) for img in os.listdir(FRACTAL_PATH) \
                      if (img[-4:] in ['.png', '.jpg']) and ('fix' not in img)])
    image_names = []
    f, axes = plt.subplots(1, len(img_list)+1, sharey = False)
    
    # Fractal plot
    for i_index, img in enumerate(img_list):
      image_names.append(img.split('/')[-1].replace('.png', '').split('_')[-1])
      image = plt.imread(img)
      axes[i_index].imshow(image)
      axes[i_index].set_xticks([])
      axes[i_index].set_yticks([])
      axes[i_index].set(xlabel=image_names[i_index])
      for spine in axes[i_index].spines.values():
        spine.set_color(COLOR_LIST[i_index])
        spine.set_linewidth(2)

    # Luminance plot
    image_brightness = calculate_brightness(img_list)
    axes[-1].bar(np.arange(len(image_brightness)), image_brightness, 
                 color=COLOR_LIST,
                 ec='black')
    axes[-1].set_xticks([])
    axes[-1].set_yticks([])
    axes[-1].set_title('Luminance', fontsize=10)

    # Make folder for each date
    DATE_SAVE_PATH = os.path.join(TRACKER_PATH, 'figures', date_formatted)
    if os.path.exists(DATE_SAVE_PATH) == False:
      os.mkdir(DATE_SAVE_PATH)
    img_save_path = os.path.join(DATE_SAVE_PATH, '_fractals')
    print(' Saving figures to: {}'.format(DATE_SAVE_PATH))
    print('  _fractals.png saved.')
    f.set_size_inches(4.5, 1.33)
    plt.savefig(img_save_path, dpi=150, bbox_inches='tight', pad_inches=0.1)
    plt.close()

  # Make folder for all dates
  if combine_dates == True:
    all_dates = '_'.join(dates_formatted)
    FIGURE_SAVE_PATH = os.path.join(TRACKER_PATH, 'figures', all_dates)
    print('Save folder for combined dates: {}'.format(FIGURE_SAVE_PATH))
    if os.path.exists(FIGURE_SAVE_PATH) == False:
      os.mkdir(FIGURE_SAVE_PATH)
  else:
    FIGURE_SAVE_PATH = DATE_SAVE_PATH
  return FIGURE_SAVE_PATH
