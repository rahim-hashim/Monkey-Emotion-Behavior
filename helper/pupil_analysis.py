import numpy as np
import matplotlib.pyplot as plt

def pupil_valence_no_blink(session_df_correct, session_obj):
	"""
	pupil_valence_no_blink plots pupil size by valence on trials without blinks only

	Args:
		session_df_correct (pd.DataFrame): dataframe of correct trials
		session_obj (Session): session object

	Returns:
		fig (plt.figure): figure of pupil size by valence on trials without blinks only
	"""
	import seaborn as sns
	session_df_correct['pupil_mean'] = session_df_correct['pupil_window'].apply(lambda x: np.mean(x))
	df = session_df_correct[(session_df_correct['fractal_count_in_block'] > 10) & 
													(session_df_correct['blink_in_window'] == 0)]
	# dates_selected = ['220913']
	# df = df.loc[(df['date'].isin(dates_selected))]
	fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5), sharex=True, sharey=False)
	ax = sns.boxplot(ax=ax1, x='valence', y='pupil_mean', data=df, 
							palette=reversed(session_obj.valence_colors))
	ax = sns.barplot(ax=ax2, x='valence', y='pupil_mean', data=df, 
							palette=reversed(session_obj.valence_colors), ec='black', lw=1)
	ax1.set_xlabel('Outcome', fontsize=14)
	ax1.set_ylabel('Pupil Diameter (mm)', fontsize=14)
	ax1.set_title('Pupil Diameter by Outcome', fontsize=20)
	ax1.set_xticklabels(['Large Airpuff', 'Small Airpuff', 'Small Reward', 'Large Reward'], fontsize=12)
	ax1.set_yticks([6500, 7000, 7500, 8000, 8500, 9000])
	ax1.set_yticklabels([6500, 7000, 7500, 8000, 8500, 9000], fontsize=12)
	ax1.set_ylim([6500, 9000])
	ax2.set_xlabel('Outcome', fontsize=14)
	ax2.set_ylabel('Pupil Diameter Mean (mm)', fontsize=14)
	ax2.set_title('Pupil Diameter by Outcome', fontsize=20)
	ax2.set_xticklabels(['Large Airpuff', 'Small Airpuff', 'Small Reward', 'Large Reward'], fontsize=12)
	ax2.set_yticks([6500, 7000, 7500, 8000])
	ax2.set_yticklabels([6500, 7000, 7500, 8000], fontsize=12)
	ax2.set_ylim([6500, 8000])
	plt.setp(ax.patches, linewidth=2)
	plt.show()
	print(df.groupby('valence')['pupil_mean'].count())

def find_first_blink(row):
	blink_list = row['blink_count_window']
	blinks = [b_index for b_index, bin in enumerate(blink_list) if bin != 0]
	if blinks:
		return blinks[0]
	else:
		return np.nan

def preblink_window(row):
	blink_index = row['first_blink']
	if blink_index and blink_index > 300:
		bin = int(blink_index)
		pupil_pre_CS = np.mean(row['pupil_pre_CS_mean'])
		pupil_mean = np.mean(row['pupil_window'][bin-200:bin-50])
		# pupil_mean = pupil_window - pupil_pre_CS
	else:
		pupil_mean = np.nan
	return pupil_mean

def pupil_preblink(session_df_correct, session_obj):
	"""
	pupil_preblink plots the pupil diameter before the first blink in a trial

	Args:
		session_df_correct (dataframe): dataframe containing all correct trials
		session_obj (Session): session object containing session metadata

	Returns:
		plot: plot of pupil diameter before the first blink in a trial
	"""
	import seaborn as sns
	session_df_correct['pupil_pre_CS_mean'] = session_df_correct['pupil_pre_CS'].apply(lambda x: np.mean(x))
	session_df_correct['first_blink'] = session_df_correct.apply(find_first_blink, axis=1)
	session_df_correct['pupil_preblink'] = session_df_correct.apply(preblink_window, axis=1)
	df = session_df_correct[(session_df_correct['fractal_count_in_block'] > 10) & 
													(session_df_correct['pupil_preblink'] != np.nan)]
	print(df.groupby(['valence'])[['pupil_preblink']].count())
	ax = sns.barplot(x='valence', y='pupil_preblink', data=df, 
							palette=reversed(session_obj.valence_colors), ec='black')
	ax.set_xlabel('Outcome', fontsize=14)
	ax.set_ylabel('Pupil Diameter (mm)', fontsize=14)
	ax.set_title('Pupil Diameter by Outcome', fontsize=20)
	ax.set_xticklabels(['Large Airpuff', 'Small Airpuff', 'Small Reward', 'Large Reward'], fontsize=12)
	y_range = list(range(6500, 9000, 500))
	ax.set_yticks(y_range)
	ax.set_yticklabels(y_range, fontsize=12)
	ax.set_ylim([6500, 8500])
	plt.setp(ax.patches, linewidth=2)
	plt.show()