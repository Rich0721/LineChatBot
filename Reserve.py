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

def main():
	flag = True
	reserve = []
	open = True
	week = ["Sun","Mon","Tue","Web"] # These day of week update a day.
	store = {}
	today = datetime.now().strftime("%Y%m%d")
	read = True

	while(flag):
		if open:
			dateDict,dateList = BookDate()
			open = False
		elif "23:00" == datetime.now().strftime("%H:%M"):
			dateDict,dateList = BookDate()
			
			read = True
			if datetime.now().strftime("%a") in week:
				while read:
					temp = ConnectDatabase.searchOneWayData(dateList[-1])
					if temp != None:
						reserve.append(temp)
					else:
						read = False
			elif "Thu" == datetime.now().strftime("%a"):
				for i in range(3):
					read = True
					while read:
						temp = ConnectDatabase.searchOneWayData(dateList[i-1])
						if temp != None:
							reserve.append(temp)
						else:
							read = False
			time.sleep(60)
			print(reserve)
		elif today != datetime.now().strftime("%Y%m%d"):
			today = datetime.now().strftime("%Y%m%d")
			if len(reserve):
				for ReserveData in reserve:
					ReserveData['startDate'] = dateDict[ReserveData['startDate']]
					data, times = bookOneWay(information=ReserveData,choice_train=ReserveData['reserve'])
					store['userName'] = ConnectDatabase.returnUserName(ReserveData['id'])
					print(store)
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
			ConnectDatabase.ReserveData(today,delete=True)
			reserve.clear()
			print(read)
		else:
			for date in dateList:
				information = ConnectDatabase.searchOneWayData(date)
				if information != None:
					information['startDate'] = dateDict[information['startDate']]
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

main()
