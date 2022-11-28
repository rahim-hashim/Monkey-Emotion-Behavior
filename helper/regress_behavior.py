import os
import numpy as np
import pandas as pd
from pprint import pprint
from Session import Session
from Path import Path
import matplotlib.pyplot as plt
from add_fields import add_fields
pd.options.mode.chained_assignment = None  # default='warn'

from sklearn.model_selection import train_test_split, cross_validate, ShuffleSplit
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_absolute_error, mean_squared_error


def regress_behavior(df, session_obj) -> None:
	'''
	regress_behavior regresses all selected behavioral measures
	(i.e. lick_duration, blink_duration) to predict the valence of the stimuli

	Args:
		- df: 
		- session_obj: 

	Output:
		- regression coefficients and r-squared values for each parameter
	'''

	def reward_airpuff_mag(row):
		if row['reward_mag'] == 0:
			if row['airpuff_mag'] == 1:
				return -1
			else:
				return -0.5
		else:
			if row['reward_mag'] == 1:
				return 1
			else:
				return 0.5

	# 1. plot distribution of licks and blinks
	# 2. see if more normal, poisson, or gamma distribution for GLM fitting
	# 3. also add field for early vs. late in block (or in quartiles)
	# 4. Z-score lick and blink
	# 5. fit SVM to binary (reward vs. aversive) for classification
	# 6. add fractal identity (A = 1, 0, 0....; B = 0, 1, 0....) -> one hot encoder for sklearn

	print('Predicting valence of stimuli')
	X = df[['fractal_count_in_block', 
					'lick_duration', 
					'blink_duration_offscreen', 
					'reward_1_back', 'reward_2_back', 
					'airpuff_1_back', 'airpuff_2_back']]
	X = X.iloc[2:] # reward_n_back and airpuff_n_back shifted by 2 trials
	df['valence'] = df.apply(reward_airpuff_mag, axis=1)
	y = df['valence'].iloc[2:] # reward_n_back and airpuff_n_back shifted by 2 trials
	for column in X.columns:
		X[column] = (X[column] - X[column].min()) / (X[column].max() - X[column].min())
	
	regr = LinearRegression()
	regr.fit(X.values, y.values)
	print(regr.coef_)
	predicted_reward_mag = regr.predict([[0, 1, 0, 0, 0, 0, 0]])
	print(predicted_reward_mag)
	predicted_reward_mag = regr.predict([[0, 0, 1, 0, 0, 0, 0]])
	print(predicted_reward_mag)
	predicted_reward_mag = regr.predict([[0.5, 0, 1, 0, 0, 0, 0]])
	print(predicted_reward_mag)

	
	# Splitting the data into training and testing data
	regr = LinearRegression()
	ridge_regr = Ridge()

	shuffle_split = ShuffleSplit(n_splits=10, test_size=0.25)

	# Dropping any rows with Nan values
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25)
	regr.fit(X_train, y_train)
	print(regr.score(X_test, y_test))
	y_pred = regr.predict(X_test)
	mae = mean_absolute_error(y_test, y_pred)
	mse = mean_squared_error(y_test, y_pred)
	rmse = np.sqrt(mse)
	print('MAE: %.2f' % mae)
	print('MSE: %.2f' % mse)
	print('RMSE: %.2f' % rmse)

	reg_dict = cross_validate(regr, X, y, cv=shuffle_split)
	print('test_score', reg_dict['test_score'])

	reg_dict = cross_validate(ridge_regr, X, y, cv=shuffle_split)
	print('test_score', reg_dict['test_score'])

	print('Predicting lick duration')
	X_2 = df[['fractal_count_in_block', 
						'valence', 
						'reward_1_back', 'reward_2_back', 
						'airpuff_1_back', 'airpuff_2_back']]
	X_2 = X_2.iloc[2:] # reward_n_back and airpuff_n_back shifted by 2 trials
	y_2 = df['lick_duration'].iloc[2:] # reward_n_back and airpuff_n_back shifted by 2 trials
	for column in X_2.columns:
		X_2[column] = (X_2[column] - X_2[column].min()) / (X_2[column].max() - X_2[column].min())
	
	regr_2 = LinearRegression()
	ridge_regr_2 = Ridge()
	shuffle_split_2 = ShuffleSplit(n_splits=10, test_size=0.1)

	regr_2.fit(X_2.values, y_2.values)
	print(regr_2.coef_)
	predicted_reward_mag = regr_2.predict([[0, 0.5, 0, 0, 0, 0]])
	print(predicted_reward_mag)
	predicted_reward_mag = regr_2.predict([[0, 1, 0, 0, 0, 0]])
	print(predicted_reward_mag)
	predicted_reward_mag = regr_2.predict([[0, -0.5, 0, 0, 0, 0]])
	print(predicted_reward_mag)
	predicted_reward_mag = regr_2.predict([[0, -1, 0, 0, 0, 0]])
	print(predicted_reward_mag)
	predicted_reward_mag = regr_2.score(X_2.values, y_2.values)
	print(predicted_reward_mag)

	reg_dict = cross_validate(ridge_regr_2, X_2, y_2, cv=shuffle_split_2)
	print('test_score', reg_dict['test_score'])

	# Z-score predictors (rather than normalizing)

	# print('Predicting blink duration')
	# X_3 = df[['fractal_count_in_block', 
	# 					'valence', 
	# 					'reward_1_back', 'reward_2_back', 
	# 					'airpuff_1_back', 'airpuff_2_back']]
	# X_3 = X_3.iloc[2:] # reward_n_back and airpuff_n_back shifted by 2 trials
	# y_3 = df['blink_duration_offscreen'].iloc[2:] # reward_n_back and airpuff_n_back shifted by 2 trials
	# for column in X_3.columns:
	# 	X_3[column] = (X_3[column] - X_3[column].min()) / (X_3[column].max() - X_3[column].min())
	
	# Sanity check
	df_condition = df[df['fractal_count_in_block'] > 20]
	X_4 = df_condition[['lick_duration']]
	y_4 = df_condition['valence']
	for column in X_4.columns:
		X_4[column] = (X_4[column] - X_4[column].min()) / (X_4[column].max() - X_4[column].min())
	
	reg_4 = Ridge()
	reg_dict = cross_validate(reg_4, X_4, y_4, cv=shuffle_split, return_estimator=True)
	estimators = reg_dict['estimator'][0]
	y_hat = estimators.predict(X_4.values)
	print('test_score', reg_dict['test_score'])
	plt.scatter(X_4, y_4)
	plt.scatter(X_4, y_hat)
	plt.show()