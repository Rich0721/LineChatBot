'''************************************************
Autor: Rich
Version: 2
Date: 2018/08/22
Second : 2018/08/24
Describe: User can book station and date. Distinguish
	confirm number which use machine learning's memory.
	Book one-way-thickets. 
************************************************'''


import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
from seleniumrequests import Chrome
import re
import time
from keras.models import load_model,Model
from PIL import Image
import shutil
import numpy as np

# Station and Date's data.
def BookDateAndStationData():
	
	print("Gain BookDateAndStationData start.")

	dateDict  = {}
	stationDict = {}

	# Obtain date and station.
	driver = webdriver.Chrome()
	driver.get("http://railway.hinet.net/Foreign/TW/etno1.html")
	soup = BeautifulSoup(driver.page_source,"lxml")
	date = soup.find_all(id="getin_date")
	date = date[0].find_all("option")
	station = soup.find_all(id="from_station")
	station = station[0].find_all("option")
	
	# Construct dict for station and date.
	for i in range(len(date)):
		dateDict[date[i].text[:-3]] = date[i].text

	for i in range(len(station)):
		stationDict[station[i].text[4:]] = station[i].text

	driver.close()

	print("Gain BookDateAndStationData is success.")

	return dateDict,stationDict


# Identification Number
def confirmNumber(fileName="check.jpg"):

	print("confirmNumber start.")
	LETTERSTR = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ"
	model = None
	model5 = load_model5
	model6 = load_model6
	model56 = load_model56	
	p56 = model56.predict(np.stack([np.array(Image.open(fileName))/255.0]))[0][0]
	if p56 >0.5:
		model = model6
	else:
		model = model5
	prediction = model.predict(np.stack([np.array(Image.open(fileName))/255.0]))
	answer = ""
	for predict in prediction:
		answer += LETTERSTR[np.argmax(predict[0])]
	print("confirmNumber end.")
	return answer


# Booking  
def BookingOneWay(person_id="A1234567890",date='',train_no=0,startStation="台東",toStation="台東",
	ticketNumber=1):

	print("Booking One Way start.")

	dateDict, stationDict = BookDateAndStationData()
	dateCheck = False # Date whether user can book date.
	fromStationCheck = False # Station whether user can book from_station 
	toStationCheck = False # Station whether user can book to_station

	if ((startStation != toStation) and train_no != 0 and (ticketNumber>=1) and (ticketNumber <=6)):
		
		if (date in dateDict.keys()):
			date = dateDict[date]
			dateCheck  = True

		if (startStation in stationDict.keys()):
			startStation = stationDict[startStation]
			fromStationCheck = True

		if (toStation in stationDict.keys()):
			toStation = stationDict[toStation]
			toStationCheck = True

	if (dateCheck and fromStationCheck and toStationCheck):
		
		driver = webdriver.Chrome("chromedriver.exe")
		driver.get("http://railway.hinet.net/Foreign/TW/etno1.html")
		driver.find_element_by_id("person_id").send_keys(person_id)
		driver.find_element_by_id("getin_date").send_keys(date)
		driver.find_element_by_id("from_station").send_keys(startStation)
		time.sleep(2)
		driver.find_element_by_id("to_station").send_keys(toStation)
		time.sleep(2)
		driver.find_element_by_id("train_no").send_keys(train_no)
		driver.find_element_by_id("order_qty_str").send_keys(ticketNumber)
		driver.find_element_by_css_selector('body > div.container > div.row.contents > div > form > div > div.col-xs-12 > button').click()
		
		location = driver.find_element_by_id('idRandomPic').location
		driver.save_screenshot('tmp.png')
		img = Image.open('tmp.png')
		captcha = img.crop((62, 576, 62+250, 576+77))
		captcha.convert("RGB").save('check.jpg', 'JPEG')

		answer = confirmNumber()
		print(answer)
		#driver.find_element_by_id("randInput").send_keys(answer)
		#driver.find_element_by_id("sbutton").click()

		'''if "訂票成功" in driver.page_source:
			soup = BeautifulSoup(driver.page_source,"lxml")
			Number = soup.find_all(id="spanOrderCode")
			print(Number[0].text)
		else:
			print("訂票失敗")'''


#BookingOneWay(train_no=113,\
#			startStation="台中",toStation="高雄",ticketNumber=1)