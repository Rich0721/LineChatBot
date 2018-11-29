'''************************************************
Autor: Rich
Version: 3
Date: 2018/09/15
Describe: Line chat-bot run. Reply question and check
data is true or not. And then help user book thickets.
Now, book one-way and return thickets at train numbers.
************************************************'''
from flask import Flask, request, abort
from linebot import (
	LineBotApi, WebhookHandler)
from linebot.exceptions import (
	InvalidSignatureError)
from linebot.models import (
	MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,
    TemplateSendMessage, ConfirmTemplate,PostbackTemplateAction,MessageTemplateAction
	)
import os
import time
from datetime import datetime, timedelta
import checkData,ReplyMessage,ConnectDatabase
from BookTickets import BookDateAndStationData
from Cutting_dict import cutRegisted, breakUpReturnData, backupInfromation


# Creating Flask object
app = Flask(__name__)

#Token


line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

global station,bookDate,startHourDict,endHourDict
station = {} # Train station data
bookDate = {} # Can book date
startHourDict = {}
endHourDict = {}


global information,choice,bookStep,registedStep,registedDict,searchBool
searchBool = False
information = {}
registedDict = {}
registedStep = 0
choice = 0

# Book date update.
global restart
restart = 0


@app.route("/")
def homepage():
    return "Hello world!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
	today = time.strftime("%Y%m%d",time.localtime())
	updateDate(today)
	information = {}
	backup = {}

	if ConnectDatabase.LineIDExist(data=event.source.user_id) != None:
		information = ConnectDatabase.LineIDExist(data=event.source.user_id)
	elif (ConnectDatabase.LineIDExist(data=event.source.user_id) == None):
		line_bot_api.reply_message(event.reply_token, ReplyMessage.GreetingsMessage(step=2))
		information['LineID'] = event.source.user_id
		information['registedStep'] = 0
		information['choice'] = 0
		information['bookStep'] = 0
		information['searchBool'] = False
		information['exit'] = datetime.now() + timedelta(seconds=30)
		ConnectDatabase.renewStep(information=information,insert=True)

	if (("Hi" == event.message.text) or ("hi" == event.message.text)):
		information['registedStep'] = 0
		information['choice'] = 0
		information['bookStep'] = 0
		information['searchBool'] = False
		information['exit'] = (datetime.now() + timedelta(seconds=30)).strftime('%Y-%m-%d %H:%M:%S')
		ConnectDatabase.renewStep(information=information,update=True)

	if("訂票去" in event.message.text):
		line_bot_api.reply_message(event.reply_token, ReplyMessage.GreetingsMessage(step=3))
		information['bookStep'] = 1
		ConnectDatabase.renewStep(information=information,update=True)
	elif ("未註冊" in event.message.text):
		line_bot_api.reply_message(event.reply_token,ReplyMessage.registerMessage(registedstep=1))
		information['registedStep'] = 2
	elif ("查詢訂票" in event.message.text):
		line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=1))
		information['searchBool'] = True
		information['exit'] = (datetime.now() + timedelta(seconds=30)).strftime('%Y-%m-%d %H:%M:%S')
		ConnectDatabase.renewStep(information=information,update=True)
	elif information['searchBool']:
		temp = ConnectDatabase.searchReserveData(event.message.text)
		if (temp != None):
			if (temp['success']):
				line_bot_api.reply_message(event.reply_token,TextSendMessage(text='''取票號碼:{},
					發車時間:{},取票時間:{}'''.format(temp['book_number'],temp['ride_up_date'],temp["pick_up_deadling"])))
			else:
				if temp['times'] == 6:
					line_bot_api.reply_message(event.reply_token,TextSendMessage(text="沒有空位"))
				elif temp['times'] == 5:
					line_bot_api.reply_message(event.reply_token,TextSendMessage(text="訂票失敗"))
		else:
				line_bot_api.reply_message(event.reply_token,TextSendMessage(text="沒有訂票資料"))
		ConnectDatabase.renewStep(information=information)
	elif(information['registedStep'] == 2):# Registered id step.
		if ConnectDatabase.confirmeUserName(data=event.message.text):
			information['id'] = event.message.text
			line_bot_api.reply_message(event.reply_token,ReplyMessage.registerMessage(registedstep=information['registedStep']))
			information['registedStep'] = 3
		else:
			line_bot_api.reply_message(event.reply_token,ReplyMessage.registerMessage(registedstep=4))
	elif information['registedStep'] == 3:
		if ConnectDatabase.confirmeUserName(event.message.text):
			information['userName'] = event.message.text
			line_bot_api.reply_message(event.reply_token,ReplyMessage.confrimBook(infromation=information,choice=5))
			information['registedStep'] = 4
		else:
			line_bot_api.reply_message(event.reply_token,ReplyMessage.registerMessage(registedstep=5))
	elif information['registedStep'] == 4:
		if("確認無誤" in event.message.text):
			registedDict = {}
			registedDict = cutRegisted(information)
			ConnectDatabase.register(registedDict)
			line_bot_api.reply_message(event.reply_token,ReplyMessage.registerMessage(registedstep=3))
			information['exit'] = (datetime.now() + timedelta(seconds=30)).strftime('%Y-%m-%d %H:%M:%S')
			ConnectDatabase.renewStep(information=information,update=True)
		elif("輸入錯誤" in event.message.text):
			line_bot_api.reply_message(event.reply_token,ReplyMessage.registerMessage(registedstep=1))
			information['registedStep'] = 2
	print(information)
	if("單程-車次" in event.message.text):
		information['choice'] = 1
	elif("單程-車種" in event.message.text):
		information['choice'] = 2
	elif("來回-車次" in event.message.text):
		information['choice'] = 3
	elif("來回-車種" in event.message.text):
		information['choice'] = 4

	'''*****************************
	bookStep 1: Key in registered ID.
	bookStep 2: Key in start date.
	bookStep 3: Key in orgin station.
	bookStep 4: Key in arrival station.
	bookStep 5: Choice going train type.
	bookStep 6: Key in going start-time.
	bookStep 7: Key in going end-time.
	bookStep 8: Key in going train number.
	bookStep 9: Book ticket numbers.
	bookStep 10: Key in back date.
	bookStep 11: Choice back train type.
	bookStep 12: Key in back strat-time.
	bookStep 13: Key in back end-time.
	bookStep 14: Key in back train number.
	bookStep 15: Book or store.
	******************************'''


	if((information['choice'] >= 1) and (information['choice'] <= 4)):
		if(information['bookStep'] == 1):
			line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=information['bookStep']))
			information['bookStep'] = 2
		elif(information['bookStep'] == 2):
			if ConnectDatabase.searchID(event.message.text):
				information['id'] = event.message.text
				line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=information['bookStep']))
				information['bookStep'] = 3
			else:
				line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(information['bookStep']-1)))
		elif((information['bookStep'] == 3) or (information['bookStep'] == 11)):

			if(information['bookStep'] == 3):
				if (int(today) <= int(event.message.text.replace('/',''))):
					information["startDate"] = event.message.text
					line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=information['bookStep']))
					information['bookStep'] = 4
				else:
					line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=information['bookStep']-1))
			else:
				if(int(event.message.text.replace('/','')) >= int(information['startDate'].replace('/',''))):
					information["endDate"] = event.message.text
					if(information['choice'] == 3):
						line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=14))
						information['bookStep'] = 14
					else:
						line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=information['bookStep']))
						information['bookStep'] = 12
				else:
					line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=information['bookStep']-1))   
		elif(information['bookStep'] == 4):
			if station.__contains__(event.message.text):
				information['startStation'] = station[event.message.text]
				line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=information['bookStep']))
				if((information['choice'] == 2) or (information['choice'] == 4)):
					information['bookStep'] = 5
				else:
					information['bookStep'] = 8
			else:
				line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(information['bookStep']-1)))
		elif(information['bookStep'] == 5):
			if station.__contains__(event.message.text):
				information['endStation'] = station[event.message.text]
				line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=information['bookStep']))
				information['bookStep'] = 6
			else:
				line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(information['bookStep']-1)))
		elif((information['bookStep'] == 6) or (information['bookStep'] == 12)):
			if(("1-自強號" in event.message.text) or ("2-莒光號" in event.message.text)):
				if(information['bookStep'] == 6):
					information['goingType'] = event.message.text
					line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=information['bookStep']))
					information['bookStep'] = 7
				else:
					information['backType'] = event.message.text
					line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=information['bookStep']))
					information['bookStep'] = 13
			else:
				line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(information['bookStep']-1)))
		elif((information['bookStep'] == 7) or (information['bookStep'] == 13)):
			if startHourDict.__contains__(event.message.text):
				if(information['bookStep'] == 7):
					information['goingStartHour'] = startHourDict[event.message.text]
					line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=information['bookStep']))
					information['bookStep'] = 9
				else:
					information["backStartHour"] = startHourDict[event.message.text]
					line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=information['bookStep']))
					information['bookStep'] = 14
			else:
				line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(information['bookStep']-1)))
		elif(information['bookStep'] == 8):
			if station.__contains__(event.message.text):
				information['endStation'] = station[event.message.text]
				line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=information['bookStep']))
				information['bookStep'] = 9
			else:
				line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=4))
		elif((information['bookStep'] == 9) or (information['bookStep'] == 14)):
			if((information['choice'] == 2) or (information['choice'] == 4)):
				if (endHourDict.__contains__(event.message.text)):
					if((information['bookStep'] == 9) and (endHourDict[event.message.text] != information['goingStartHour'])):
						information['goingEndHour'] = endHourDict[event.message.text]
						line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=information['bookStep']))
						information['bookStep'] = 10
					elif((information['bookStep'] == 14) and (endHourDict[event.message.text] != information['backStartHour'])):
						information['backEndHour'] =  endHourDict[event.message.text]
						line_bot_api.reply_message(event.reply_token,ReplyMessage.confrimBook(infromation=information,choice=information['choice']))
						information['bookStep'] = 15
					else:
						line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=7))    
				else:
					line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=7))
			else:
				if(information['bookStep'] == 9):
					information['goingTrain'] = event.message.text
					line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=information['bookStep']))
					information['bookStep'] = 10
				else:
					information['backTrain'] = event.message.text
					line_bot_api.reply_message(event.reply_token,ReplyMessage.confrimBook(infromation=information,choice=information['choice']))
					information['bookStep'] = 15
		elif(information['bookStep'] == 10):
			if checkData.checkTicketsNumbers(int(event.message.text)):
				information['goingticketNumbers'] = event.message.text
				if((information['choice']==1) or (information['choice']==2)):
					line_bot_api.reply_message(event.reply_token,ReplyMessage.confrimBook(infromation=information,choice=information['choice']))
					information['bookStep'] = 15
				else:
					line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=information['bookStep']))
					information['bookStep'] = 11
			else:
				line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(information['bookStep']-1)))
		#If checke is not error, program automatically distinguish booking-date whether can book.
		#If it can book then book, store to database.
		elif(information['bookStep'] == 15):
			if "確認無誤" in event.message.text:
				information['id'] = ConnectDatabase.returnIdentification(information['id'])
				if ((information['choice'] == 1) or (information['choice'] == 2)):
					if bookDate.__contains__(information['startDate']):
						information['reserve'] = information['choice']
						ConnectDatabase.insertOneWayData(data=information)
						line_bot_api.reply_message(event.reply_token,ReplyMessage.replyMessageMenu(Imme=True))
					else:
						line_bot_api.reply_message(event.reply_token,ReplyMessage.replyMessageMenu(Imme=False,oneWay=False))
						information['reserve'] = information['choice']
						ConnectDatabase.insertOneWayData(data=information)
				else:
					if ((bookDate.__contains__(information['startDate'])) and (bookDate.__contains__(information['endDate']))):
						going,back =  breakUpReturnData(information=information,choice=information['choice'])
						ConnectDatabase.insertOneWayData(data=going)
						ConnectDatabase.insertOneWayData(data=back)
						line_bot_api.reply_message(event.reply_token,ReplyMessage.replyMessageMenu(Imme=True))

					elif bookDate.__contains__(information['startDate']):
						going,back =  breakUpReturnData(information=information,choice=information['choice'])
						ConnectDatabase.insertOneWayData(data=going)
						ConnectDatabase.insertOneWayData(data=back)
						line_bot_api.reply_message(event.reply_token,ReplyMessage.replyMessageMenu(Imme=False,oneWay=True))
					else:
						line_bot_api.reply_message(event.reply_token,ReplyMessage.replyMessageMenu(Imme=False,oneWay=False))
						going,back =  breakUpReturnData(information=information,choice=information['choice'])
						ConnectDatabase.insertOneWayData(data=going)
						ConnectDatabase.insertOneWayData(data=back)
				information['bookStep'] = 0
				information['exit'] = (datetime.now() + timedelta(seconds=30)).strftime('%Y-%m-%d %H:%M:%S')
				ConnectDatabase.renewStep(information=information,update=True)
			else:
				information['bookStep'] = 1

	if ((information['bookStep'] >= 1) and (information['bookStep'] <=15)):
		information['exit'] = (datetime.now() + timedelta(seconds=30)).strftime('%Y-%m-%d %H:%M:%S')
		ConnectDatabase.renewStep(information=information,update=True)
	elif ((information['registedStep'] >= 1) and (information['registedStep'] <= 4)):
		information['exit'] = (datetime.now() + timedelta(seconds=30)).strftime('%Y-%m-%d %H:%M:%S')
		ConnectDatabase.renewStep(information=information,update=True)
    

def updateDate(today):

	global restart,station,bookDate,startHourDict,endHourDict
	update = time.strftime("%Y%m%d",time.localtime())
	if ((update != today) or (restart == 0)):
		today = update
		restart = 1
		bookDate, station, startHourDict, endHourDict= BookDateAndStationData()

if  __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='127.0.0.1', port=5000)
