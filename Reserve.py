'''************************************************
Autor: Rich
Version: 1
Date: 2018/10/10
Describe: Check Taiwan Railway's booking tickets 'time.
	If users' tickets time can book, it will booking and
	store database which users can search. 
************************************************'''

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from datetime import datetime
from datetime import timedelta
import ConnectDatabase
from BookTickets import bookOneWay
import threading


def BookDate():

	dateDict  = {}
	dateList = []

	driver = webdriver.Chrome()
	driver.get("http://railway.hinet.net/Foreign/TW/etkind1.html")
	soup = BeautifulSoup(driver.page_source,'lxml')
	date = soup.find_all(id="getin_date")
	date = date[0].find_all("option")
	for i in range(len(date)):
		dateDict[date[i].text[:-3].replace('/','')] = date[i].text
		dateList.append(date[i].text[:-3].replace('/',''))
	driver.close()
	return dateDict,dateList

def threadJob(today,date):
	store = {}
	while today == datetime.now().strftime("%Y%m%d"):
		print(date)
		information = ConnectDatabase.searchOneWayData(date)
		if information != None:
			information['startDate'] = date
			data, times = bookOneWay(information=information,choice_train=information['reserve'])
			store['userName'] = ConnectDatabase.returnUserName(information['id'])
			if len(data):
				store['book_number'] = data[0]
				store['ride_up_date'] = data[1]
				store["pick_up_deadling"] = data[2]
				store['success'] = True
			else:
				store['pick_up_deadling'] = ((datetime.now()) + timedelta(days=2)).strftime("%Y%m%d")
				store['success'] = False
			store['times'] = times
			ConnectDatabase.ReserveData(store,store=True)
			store.clear()


def constructThread(today,dateList,dateDict,varx):
	threads = []
	for i in range(len(dateList)-varx):
		threads.append(threading.Thread(target=threadJob, args=(today,dateDict[dateList[i]],)))
		threads[i].start()

	for i in range(len(dateList)-varx):
		threads[i].join()
	print("Done threads at 23:00~00:00")

def main():
	flag = True
	boot = True
	today = datetime.now().strftime("%Y%m%d")

	while(flag):
		if boot:
			dateDict,dateList = BookDate()
			boot = False
		elif "23:00" == datetime.now().strftime("%H:%M"):
			dateDict,dateList = BookDate()

			if (datetime.now().strftime("%a") == "Thu"):
				constructThread(today=today, dateList=dateList, dateDict=dateDict, varx=2)
			elif (datetime.now().strftime("%a") == "Fri"):
				constructThread(today=today, dateList=dateList, dateDict=dateDict, varx=1)
			else:
				constructThread(today=today, dateList=dateList, dateDict=dateDict, varx=0)
		else:
			constructThread(today=today, dateList=dateList, dateDict=dateDict, varx=0)

main()
