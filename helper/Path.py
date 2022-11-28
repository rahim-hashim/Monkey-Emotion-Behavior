import os

class Path:
	def __init__(self, ROOT, EXPERIMENT, TASK):

		# Data Paths
		self.RAW_DATA_PATH = os.path.join('data', 'raw', 'data_'+TASK)
		self.PROCESSED_DATA_PATH = os.path.join('data', 'processed', 'processed_'+TASK)

		# Current and Target Path
		self.CURRENT_PATH = os.path.join(ROOT, self.RAW_DATA_PATH)
		self.TARGET_PATH = os.path.join(ROOT, self.PROCESSED_DATA_PATH)

		# Figure Paths
		self.FIGURE_PATH = os.path.join(ROOT, 'figures', TASK)

		# Task Path
		self.task_root = os.path.join(ROOT, 'tasks', EXPERIMENT)
		list_tasks = os.listdir(self.task_root)
		for task_type in list_tasks:
			if TASK in task_type:
				self.TASK_PATH = os.path.join(self.task_root, task_type)

		self.current_dir = os.listdir(self.CURRENT_PATH)

		# Tracker Path
		self.TRACKER_PATH = os.path.join(ROOT, 'docs', 'Tracker', 'Emotion')

		# Excel Path
		self.EXCEL_PATH = os.path.join(self.TRACKER_PATH, 'Emotion_Tracker.xlsx')

		# Video Path
		self.VIDEO_PATH = os.path.join(ROOT, 'Monkey-Emotion', 'analysis_scripts', 'Video')