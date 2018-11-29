'''************************************************
Autor: Rich
Version: 3
Date: 2018/08/22
Second : 2018/08/24
Third : 2018/09/04
Describe: User can book station and date. Distinguish
	confirm number which use machine learning's memory.
	Use train number or train kinds to book one-way-
	thickets. Return Book_Number, ride-up-date and 
	pick-up-deadline.
************************************************'''


import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
from seleniumrequests import Chrome
import re
from time import sleep
from keras.models import load_model,Model
from PIL import Image
import shutil
import numpy as np
from selenium.webdriver.common.action_chains import ActionChains


global model5,model6,model56
model5 = load_model("real_5.h5")
model6 = load_model("D:/專題/爬蟲/TrainCodeImage/Program/real_6_2.h5")
model56 = load_model("real_56.h5")



# Station and Date's data.
def BookDateAndStationData():
	
	print("Gain BookDateAndStationData start.")

	dateDict  = {}
	stationDict = {}
	startHourDict = {}
	endHourDict = {}

	# Obtain date and station.
	driver = webdriver.Chrome()
	driver.get("http://railway.hinet.net/Foreign/TW/etkind1.html")
	soup = BeautifulSoup(driver.page_source,"lxml")
	date = soup.find_all(id="getin_date")
	date = date[0].find_all("option")
	station = soup.find_all(id="from_station")
	station = station[0].find_all("option")
	startHour = soup.find_all(id="getin_start_dtime")
	startHour = startHour[0].find_all("option")
	endHour = soup.find_all(id="getin_end_dtime")
	endHour = endHour[0].find_all("option")
	
	# Construct dict for station and date.
	for i in range(len(date)):
		dateDict[date[i].text[:-3].replace('/','')] = date[i].text

	for i in range(len(station)):
		stationDict[station[i].text[4:]] = station[i].text

	for i in range(len(startHour)):
		startHourDict[startHour[i].text.replace(':','')] = startHour[i].text

	for i in range(len(endHour)):
		endHourDict[endHour[i].text.replace(':','')] = endHour[i].text

	driver.close()

	print("Gain BookDateAndStationData is success.")

	return dateDict,stationDict,startHourDict,endHourDict


# Identification Number
def confirmNumber(fileName="check.jpg"):

	print("confirmNumber start.")
	LETTERSTR = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ"
	model = None
	global model5,model6,model56
	p56 = model56.predict(np.stack([np.array(Image.open(fileName))/255.0]))[0][0]
	if p56 >0.5:
		model = model6
	else:
		model = model5
	prediction = model.predict(np.stack([np.array(Image.open(fileName))/255.0]))
	answer = ""
	for predict in prediction:
		answer += LETTERSTR[np.argmax(predict[0])]
	print(answer)
	print("confirmNumber end.")
	return answer


# Book one-way tickets. If train number isn't equal zero that user use train number booking, use train type. 
def bookOneWay(information,choice_train):
	
	print("bookOneWay start")
	success = False
	times = 0
	Numbers = []
	driver = webdriver.Chrome("chromedriver.exe")

	while ((not success) and (times < 5)):
		
		if(choice_train == 1):
			driver.get("http://railway.hinet.net/Foreign/TW/etno1.html")
			driver.find_element_by_id("train_no").send_keys(information['goingTrain'])
			driver.find_element_by_id("person_id").send_keys(information["id"])
			sleep(1)
			# If train number is special train and  ticket numbers equal four, booking table seat.
			# If train number is special train and tickets is not equal to four, booking normal seat.
			if('附掛桌型座位' in driver.page_source):
				if(int(information['goingticketNumbers']) == 4):
					driver.find_element_by_id("z_order_qty_str").send_keys(information['goingticketNumbers'])
				else:
					driver.find_element_by_id("n_order_qty_str").send_keys(information['goingticketNumbers'])
			elif('附掛親子車廂' in driver.page_source):
				driver.find_element_by_id("n_order_qty_str").send_keys(information['goingticketNumbers'])
			else:
				driver.find_element_by_id("order_qty_str").send_keys(information['goingticketNumbers'])
		else:
			driver.get("http://railway.hinet.net/Foreign/TW/etkind1.html")
			driver.find_element_by_id("person_id").send_keys(information["id"])
			driver.find_element_by_id("train_type").send_keys(information['goingType'])
			driver.find_element_by_id("getin_start_dtime").send_keys(information['goingStartHour'])
			driver.find_element_by_id("getin_end_dtime").send_keys(information['goingEndHour'])
			sleep(1)
			driver.find_element_by_id("order_qty_str").send_keys(information['goingticketNumbers'])

		driver.find_element_by_id("from_station").send_keys(information["startStation"])
		sleep(1)
		driver.find_element_by_id("to_station").send_keys(information["endStation"])
		sleep(1)
		driver.find_element_by_id("getin_date").send_keys(information["startDate"])

		driver.find_element_by_css_selector('body > div.container > div.row.contents > div > form > div > div.col-xs-12 > button').click()

		driver.save_screenshot('tmp.png')
		img = Image.open('tmp.png')
		captcha = img.crop((62, 576, 62+250, 576+77))
		captcha.convert("RGB").save('check.jpg', 'JPEG')
		answer = confirmNumber()

		driver.find_element_by_id("randInput").send_keys(answer)
		driver.find_element_by_id("sbutton").click()

		if "訂票成功" in driver.page_source:
			success = True
			soup = BeautifulSoup(driver.page_source,"lxml")
			Numbers.append(soup.find_all(id="spanOrderCode")[0].text) # Pick up tickets numbers
			Numbers.append(soup.find_all('span',{'class':"text-muted"})[5].text) # Ride up date
			Numbers.append(soup.find_all('p',{'class':"gray01"})[0].find('span').text) # Pick up deadline
		elif (("您要預訂車票的總座位數為零" in driver.page_source) or ("無剩餘座位" in driver.page_source)):
			times = 6
		else:
			times += 1
	driver.close()
	return Numbers,times
