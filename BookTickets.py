'''************************************************
Autor: Rich
Version: 3
Date: 2018/08/22
Second : 2018/08/24
Third : 2018/09/04
Describe: User can book station and date. Distinguish
	confirm number which use machine learning's memory.
	Book train number and train kinds one-way-thickets
	or return tickets. 
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
from selenium.webdriver.common.action_chains import ActionChains



specialTrain = ['280','282','288','271','273','283','111','133',
	'110','136','401','411','425','431','445','447','406','412',
	'422','432','438','448','211','221','223','225','237','247',
	'207','202','218','222','238','248','232','248','232','252',
	'5932','5931']

model5 = load_model("D:/專題/爬蟲/TrainCodeImage/Program/real_5_2.h5")
model6 = load_model("D:/專題/爬蟲/TrainCodeImage/Program/real_6_2.h5")
model56 = load_model("D:/專題/爬蟲/TrainCodeImage/Program/real_56_2.h5")


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
		dateDict[date[i].text[:-3]] = date[i].text

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


# Book one-way tickets. If train number isn't equal zero that user use train number booking, use train type. 
def bookOneWay(information,choice_train):
	
	print("bookOneWay start")
	Numbers = []
	driver = webdriver.Chrome("chromedriver.exe")
	if(choice_train == 1):
		driver.get("http://railway.hinet.net/Foreign/TW/etno1.html")
		driver.find_element_by_id("train_no").send_keys(information['goingTrain'])
		driver.find_element_by_id("person_id").send_keys(information["id"])
		time.sleep(1)
		if(information['goingTrain'] in specialTrain):
			driver.find_element_by_id("n_order_qty_str").send_keys(information['ticketNumbers'])
		elif((information['goingTrain'] in specialTrain) and (int(information["ticketNumbers"]) == 4 )):
			driver.find_element_by_id("z_order_qty_str").send_keys(information['ticketNumber'])
		else:
			driver.find_element_by_id("order_qty_str").send_keys(information['ticketNumbers'])
	else:
		driver.get("http://railway.hinet.net/Foreign/TW/etkind1.html")
		driver.find_element_by_id("person_id").send_keys(information["id"])
		driver.find_element_by_id("train_type").send_keys(information['goingType'])
		driver.find_element_by_id("getin_start_dtime").send_keys(information['goingStartHour'])
		driver.find_element_by_id("getin_end_dtime").send_keys(information['goingEndHour'])
		time.sleep(1)
		driver.find_element_by_id("order_qty_str").send_keys(information['ticketNumbers'])

	driver.find_element_by_id("from_station").send_keys(information["startStation"])
	time.sleep(1)
	driver.find_element_by_id("to_station").send_keys(information["endStation"])
	time.sleep(1)
	driver.find_element_by_id("getin_date").send_keys(information["startDate"])

	driver.find_element_by_css_selector('body > div.container > div.row.contents > div > form > div > div.col-xs-12 > button').click()

	driver.save_screenshot('tmp.png')
	img = Image.open('tmp.png')
	captcha = img.crop((62, 576, 62+250, 576+77))
	captcha.convert("RGB").save('check.jpg', 'JPEG')
	answer = confirmNumber()
	
	driver.find_element_by_id("randInput").send_keys(answer)
	driver.find_element_by_id("sbutton").click()

	'''if "訂票成功" in driver.page_source:
		soup = BeautifulSoup(driver.page_source,"lxml")
		Number = soup.find_all(id="spanOrderCode")
		Numbers.append(Number[0].text)
		print(Numbers)
		return True,Numbers
	else:
		return False,Number'''


def bookRetrun(information,choice_train):
	print("bookRetrun Start")
	Numbers = []
	driver = webdriver.Chrome("chromedriver.exe")
	if(choice_train == 1):
		driver.get("http://railway.hinet.net/Foreign/TW/etno_roundtrip.html")
		driver.find_element_by_id("train_no").send_keys(information['goingTrain'])
		driver.find_element_by_id("train_no2").send_keys(information['backTrain'])
		time.sleep(1)
		if(information['goingTrain'] in specialTrain):
			driver.find_element_by_id("n_order_qty_str").send_keys(information['ticketNumbers'])
		elif((information['goingTrain'] in specialTrain) and (int(information["ticketNumbers"]) == 4 )):
			driver.find_element_by_id("z_order_qty_str").send_keys(information['ticketNumber'])
		else:
			driver.find_element_by_id("order_qty_str").send_keys(information['ticketNumbers'])
		
		if(information['backTrain'] in specialTrain):
			driver.find_element_by_id("n_order_qty_str2").send_keys(information['ticketNumbers'])
		elif((information['backTrain'] in specialTrain) and (int(information["ticketNumbers"]) == 4 )):
			driver.find_element_by_id("z_order_qty_str2").send_keys(information['ticketNumber'])
		else:
			driver.find_element_by_id("order_qty_str2").send_keys(information['ticketNumbers'])
	else:
		driver.get("http://railway.hinet.net/Foreign/TW/etkind_roundtrip.html")
		driver.find_element_by_id("train_type").send_keys(information['goingType'])
		driver.find_element_by_id("getin_start_dtime").send_keys(information['goingStartHour'])
		driver.find_element_by_id("getin_end_dtime").send_keys(information['goingEndHour'])
		time.sleep(1)
		driver.find_element_by_id("train_type2").send_keys(information['backType'])
		driver.find_element_by_id("getin_start_dtime2").send_keys(information['backStartHour'])
		driver.find_element_by_id("getin_end_dtime2").send_keys(information['backEndHour'])
		time.sleep(1)
		driver.find_element_by_id("order_qty_str").send_keys(information['ticketNumbers'])
		driver.find_element_by_id("order_qty_str2").send_keys(information['ticketNumbers'])


	driver.find_element_by_id("person_id").send_keys(information["id"])
	driver.find_element_by_id("from_station").send_keys(information["startStation"])
	time.sleep(1)
	driver.find_element_by_id("to_station").send_keys(information["endStation"])
	time.sleep(1)
	driver.find_element_by_id("getin_date").send_keys(information["startDate"])
	driver.find_element_by_id("getin_date2").send_keys(information["endDate"])

	driver.find_element_by_css_selector('body > div.container > div.row.contents > div > form > div > div.col-xs-12 > button').click()

	driver.save_screenshot('tmp.png')
	img = Image.open('tmp.png')
	captcha = img.crop((62, 576, 62+250, 576+77))
	captcha.convert("RGB").save('check.jpg', 'JPEG')
	answer = confirmNumber()
	
	driver.find_element_by_id("randInput").send_keys(answer)
	driver.find_element_by_id("sbutton").click()
	time.sleep(5)

	'''if "訂票成功" in driver.page_source:
		soup = BeautifulSoup(driver.page_source,"lxml")
		Number = soup.find_all(id="spanOrderCode")
		Numbers.append(Number[0].text)
		Number = soup.find_all(id="spanOrderCode2")
		Numbers.append(Number[0].text)
		print(Numbers)
		return True,Numbers
	else:
		print(Numbers)
		return False,Numbers'''

	print('bookRetrun end.')

information={
	"id":"",
	"startDate":"2018/09/06【四】",
	"endDate":"2018/09/10【一】",
	"goingStartHour":"09:00",
	"goingEndHour":"10:00",
	"backStartHour":"23:00",
	"backEndHour":"23:59",
	"goingTrain":"116",
	"backTrain":"113",
	"goingType":"1-自強號",
	"backType":"2-莒光號",
	"startStation":"185-高雄",
	"endStation":"146-台中",
	"ticketNumbers":"1"
	}

bookRetrun(information,choice_train=1)

#bookOneWay(person_id="A123456789",date="2018/09/01",train_no=122,startStation="高雄",toStation="台北",ticketNumber=1)

