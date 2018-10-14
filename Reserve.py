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
import ConnectDatabase

flag = True
today = time.strftime("%Y%m%d",time.localtime())
bookInformation = []

def BookDate(day):

	ReserveDates = [] 

	driver = webdriver.Chrome()
	driver.get("http://railway.hinet.net/Foreign/TW/etkind1.html")
	soup = BeautifulSoup(driver.page_source,'lxml')
	date = soup.find_all(id="getin_date")
	date = date[0].find_all("option")

	if ((day == "Mon") or (day == "Tue") or (day == "Web")\
		or (day == "Sun")): 

		infors = ConnectDatabase.searchOneWayData(data=date[-1].text[:-3]) # Gain can book information
		for infro in infors:
			infor['startDate'] = date[-1].text # Modify date to Taiwan Railway's website's formal
			ReserveDates.append(infro)


	elif(day == "Thu"):

		for i in range(3):

			infors = ConnectDatabase.searchOneWayData(date[i-3].text[:-3]) # Gain can book information
			for infro in infors:
				infor['startDate'] = date[i-3].text # Modify date to Taiwan Railway's website's formal
				ReserveDates.append(infro)

	driver.close()

	return ReserveDates

def main():
	while(flag):

		if "23:00" == time.strftime("%H:%M",time.localtime()):
			information = BookDate(day=time.strftime("%a",time.localtime()))
			time.sleep(60)
		elif today != time.strftime("%Y%m%d",time.localtime()):
			today = time.strftime("%Y%m%d",time.localtime())
			for ReserveDate in information:
				success = False
				times = 0
				while not success:
					


#x = BookDate(day=today)
#y = list(x.keys())
#print(y)