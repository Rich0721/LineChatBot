from ConnectDatabase import Overtime
from datetime import datetime, timedelta
from time import sleep
flag = True


while flag:
	print((datetime.now() + timedelta(seconds=30)).strftime('%Y-%m-%d %H:%M:%S'))
	Overtime(time=(datetime.now() + timedelta(seconds=30)).strftime('%Y-%m-%d %H:%M:%S'))
