from datetime import datetime, timedelta

def calculate_end_time(start_time, length_trial):
	'''
	calculate_end_time takes in start_time, formats it to an
	ISO-formatted datetime and calculates the trial end_time
	based on length_trial

	Args
		- start_time (str): the trial_absolute_start time
		- length_trial (float): the length of the trial (in milliseconds)

	Returns
		- start_datetime (datetime): the trial start datetime
		- end_datetime (datetime): the trial end datetime
	'''

	year = str(int(start_time[0]))
	month = str(int(start_time[1]))
	# to converto from ISO formatting, datetime must be
	# in form YY-MM-DD hh:mm:ss.sss
	if int(month) < 10: # zero padding
		month = '0' + month
	day = str(int(start_time[2]))
	if int(day) < 10: # zero padding
		day = '0' + day
	hour = str(int(start_time[3]))
	if int(hour) < 10: # zero padding
		hour = '0' + hour
	minute = str(int(start_time[4]))
	if int(minute) < 10: # zero padding
			minute = '0' + minute
	second = str(start_time[5][0])
	if float(second) < 10: # zero padding
			second = '0' + second
	length_ms_str = len(second.split('.')[1])
	if length_ms_str < 3:
		for i in range(3 - length_ms_str): 
			second = second + '0' # zero padding on end
	if length_ms_str > 3:
		second = second[:6] # shortening millisecond to 3 digit precision

	date_str = '-'.join([year, month, day])
	time_str = ':'.join([hour, minute, second])
	start_datetime_str = '{} {}'.format(date_str, time_str)

	start_datetime = datetime.fromisoformat(start_datetime_str)
	end_datetime = start_datetime + timedelta(milliseconds=length_trial)
	return start_datetime, end_datetime