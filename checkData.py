'''******************************************************
Author: Rich
Version: 2
First_Date: 2018/08/22
Second_Date: 2018/08/23
Describe: Check user's key in data whether correct. The data
	contain Identification Number, date, station, time, and 
	thicket numbers so all program return "true" or not.
*********************************************************'''
import time

def checkIdentificationNumber(id):
	if (len(id) == 10):
		return True
	return False

def checkDict(data,Dict):
	if Dict.__contains__(date):
		return True
	return False

def checkTicketsNumbers(num):
	if ((num>=1) and (num<=6)):
		return True
	return False

def checkTime(lastTime):
	current = time.strftime("%Y%m%d%H%M%S",time.localtime())
	diff = int(current) - int(lastTime)
	if (diff >=25):
		return True
	return False
