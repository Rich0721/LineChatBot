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
import checkData,BookTickets,ReplyMessage,ConnectDatabase

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


global information,choice,bookStep,registedStep,registedDict
information={
    "id":"",
    "startDate":"",
    "endDate":"",
    "goingStartHour":"",
    "goingEndHour":"",
    "backStartHour":"",
    "backEndHour":"",
    "goingTrain":"",
    "backTrain":"",
    "startStation":"",
    "endStation":"",
    "goingticketNumbers":"",
    "backticketNumbers":""
    }

registedDict = {
    "id":"",
    "userName":""
}


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
    global information,choice,bookStep,registedStep,registedDict

    # Step-1: User choice what does he(she) doing now.
    if ((event.message.text  == "Hi") or (event.message.text == "你好")):
        line_bot_api.reply_message(event.reply_token, ReplyMessage.GreetingsMessage(step=2))
        registedStep = 1
        choice = 0
    elif("訂票去" in event.message.text):
        line_bot_api.reply_message(event.reply_token, ReplyMessage.GreetingsMessage(step=3))
        bookStep = 1
        registedStep = 0
        choice = 0
    elif(("未註冊" in event.message.text) or (registedStep == 1)):
        line_bot_api.reply_message(event.reply_token,ReplyMessage.registerMessage(registedstep=1))
        registedStep = 2
        choice = 0
    # Registered id step.
    elif(registedStep == 2):
        registedDict['id'] = event.message.text
        line_bot_api.reply_message(event.reply_token,ReplyMessage.registerMessage(registedstep=registedStep))
        registedStep = 3
    elif registedStep == 3:
        if ConnectDatabase.confirmeID(registedDict):
            registedDict['userName'] = event.message.text
            line_bot_api.reply_message(event.reply_token,ReplyMessage.confrimBook(infromation=registedDict,choice=5))
            registedStep = 4
        else:
            line_bot_api.reply_message(event.reply_token,ReplyMessage.registerMessage(registedstep=4))
            registedstep = 3
    elif registedStep == 4:
        if("確認無誤" in event.message.text):
            ConnectDatabase.register(registedDict)
            line_bot_api.reply_message(event.reply_token,ReplyMessage.registerMessage(registedstep=registedStep))
            registedStep = 0
            registedDict.clear()
        elif("輸入錯誤" in event.message.text):
            line_bot_api.reply_message(event.reply_token,ReplyMessage.registerMessage(registedstep=1))
            registedstep = 1


    if("單程-車次" in event.message.text):
        choice = 1
    elif("單程-車種" in event.message.text):
        choice = 2
    elif("來回-車次" in event.message.text):
        choice = 3
    elif("來回-車種" in event.message.text):
        choice = 4

    if((choice >= 1) and (choice <= 4)):
        if(bookStep == 1):
            line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
            bookStep = 2
        elif(bookStep == 2):
            if ConnectDatabase.searchID(event.message.text):
                information['id'] = event.message.text
                line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                bookStep = 3
            else:
                line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(bookStep-1)))
        elif((bookStep == 3) or (bookStep == 11) or (bookStep == 14)):
            if bookDate.__contains__(event.message.text):
                if(bookStep == 3):
                    information["startDate"] = bookDate[event.message.text]
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                    bookStep = 4
                else:
                    information["endDate"] = bookDate[event.message.text]
                    if(bookStep == 11):
                        line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                        bookStep = 12
                    else:
                        line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                        bookStep = 15
            else:
                line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(bookStep-1)))
        elif(bookStep == 4):
            if station.__contains__(event.message.text):
                information['startStation'] = station[event.message.text]
                line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                if(choice == 2):
                    bookStep = 5
                else:
                    bookStep = 8
            else:
                line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(bookStep-1)))
        elif(bookStep == 5):
            if station.__contains__(event.message.text):
                information['endStation'] = station[event.message.text]
                line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                bookStep = 6
            else:
                line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(bookStep-1)))
        elif(bookStep == 6):
            if(("1-自強號" in event.message.text) or ("2-莒光號" in event.message.text)):
                information['goingTrain'] = event.message.text
                line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                bookStep = 7
            else:
                line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(bookStep-1)))
        elif((bookStep == 7) or (bookStep == 12)):
            if startHourDict.__contains__(event.message.text):
                if(bookStep == 7):
                    information['goingStartHour'] = startHourDict[event.message.text]
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                    bookStep = 9
                else:
                    information["backStartHour"] = startHourDict[event.message.text]
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                    bookStep = 13
            else:
                line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(bookStep-1)))
        elif(bookStep == 8):
            if station.__contains__(event.message.text):
                information['endStation'] = station[event.message.text]
                line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                bookStep = 9
            else:
                line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=4))
        elif((bookStep == 9) or (bookStep == 13) or (bookStep == 15)):
            if((choice == 2) or (choice == 4)):
                if endHourDict.__contains__(event.message.text):
                    if(bookStep == 9):
                        information['goingEndHour'] = event.message.text
                        line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                    else:
                        information['backEndHour'] = event.message.text
                        line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                else:
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=7))
            else:
                if(bookStep == 9):
                    information['goingTrain'] = event.message.text
                else:
                    information['backTrain'] = event.message.text
                line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))

            if((choice == 1) or (choice == 2) or (bookStep > 10)):
                bookStep = 16
            else:
                bookStep = 10
        elif(bookStep == 10):
            if checkData.checkTicketsNumbers(int(event.message.text)):
                information['goingticketNumbers'] = event.message.text
                line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                if(choice == 3):
                    bookStep = 14
                else:
                    bookStep = 11
            else:
                line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(bookStep-1)))
        elif(bookStep == 16):
            if(choice <= 2):
                information['goingticketNumbers'] = event.message.text
            else:
                information['backticketNumbers'] = event.message.text
            line_bot_api.reply_message(event.reply_token,ReplyMessage.confrimBook(infromation=information,choice=choice))


    
def updateDate(today):

    global station,bookDate,startHourDict,endHourDict,restart
    update = time.strftime("%Y%m%d",time.localtime())
    if ((update != today) or (restart == 0)):
        today = update
        restart = 1
        bookDate, station, startHourDict, endHourDict= BookTickets.BookDateAndStationData()

if  __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=5000)
