import os
import math
import numpy as np
import pandas as pd
from scipy import signal
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, ttest_ind_from_stats, linregress
import warnings
warnings.filterwarnings("ignore")
from matplotlib.offsetbox import AnchoredText

def lick_blink_linear(df, session_obj):
	"""
	Plots and calculates the linear relationship
	between lick rate and blink duration for 
	a given trial 
	"""
	FIGURE_SAVE_PATH = session_obj.figure_path
	COLORS = session_obj.valence_colors
	import seaborn as sns
	
	f, ax = plt.subplots(1,1, figsize=(4,4))

	# Plot regression line from all valences
	x_all = np.array(df['lick_duration'].tolist())/5
	y_all = df['blink_duration_offscreen'].tolist()
	sns.regplot(x_all, y_all, color='black', label='all', ax=ax, scatter=False)
	slope, intercept, r_value, p_value, std_err = linregress(x_all, y_all)
	text = 'R-Value: {} | P-Value: {:.3g}'.format(round(r_value, 3), p_value)
	anchored_text = AnchoredText(text,
															 loc='lower center',
															 frameon=False)
	ax.add_artist(anchored_text)
	# plt.gcf().text(1, 1.1, text, fontsize=14) 

	# Plot each valence data 
	for df_index, valence in enumerate(sorted(df['valence'].unique(), reverse=True)):

		df_valence = df[df['valence'] == valence]

		# valence-specific session lick/blink data
		x = np.array(df_valence['lick_duration'].tolist())/5
		y = df_valence['blink_duration_offscreen'].tolist()

		color = COLORS[valence]
		sns.regplot(x=x, y=y, color=color, label=valence, ax=ax, ci=None)
	
	plt.ylim([-0.175, 1.1])
	yticks = np.round(np.arange(0, 1.2, 0.2), 2)
	plt.yticks(yticks, yticks)
	plt.legend(loc='upper right', labels=['all'], fontsize=10, frameon=False)
	plt.xlabel('Norm Lick Duration')
	plt.ylabel('Norm Blink Duration')
	plt.title('Lick vs Blink Duration')
	fig_name = 'lick_vs_blink'
	img_save_path = os.path.join(FIGURE_SAVE_PATH, fig_name)
	f.savefig(img_save_path, dpi=150, bbox_inches='tight', transparent=True)
	print('  {}.png saved.'.format(fig_name))
	plt.close('all')