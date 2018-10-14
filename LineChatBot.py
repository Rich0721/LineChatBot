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
CHANNEL_ACCESS_TOKEN = "CP3lJUZTyFc8pA4hV5aS7nIUxtzbEyE+YVyU8XuA1lakCjxMQtw8XxydWQU8SZtGYF9No+vjod+dFnKNuVU86HtKem2wTwQOUeI8cSQK/wCMjA4LfzQEwHHrBHJ4rTQFiZdFGKtFaccXwFD5eMlU4wdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "828d49983f0de27995c84fbbf00c20f8"

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

global station,bookDate,startHourDict,endHourDict
station = {} # Train station data
bookDate = {} # Can book date
startHourDict = {}
endHourDict = {}


global information,choice,bookStep,registedStep,registedDict
information = {}
registedDict = {}


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
    backup = {}
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
        elif((bookStep == 3) or (bookStep == 11)):

            if(bookStep == 3):
                if (int(today) <= int(check.replace('/',''))):
                    information["startDate"] = event.message.text
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                    bookStep = 4
                else:
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=bookStep-1))
            else:
                if(int(event.message.text.replace('/','')) < int(information['startDate'].replace('/',''))):
                    information["endDate"] = event.message.text
                    if(choice == 3):
                        line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=14))
                        bookStep = 14
                    else:
                        line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                        bookStep = 12
                else:
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=bookStep-1))   
        elif(bookStep == 4):
            if station.__contains__(event.message.text):
                information['startStation'] = station[event.message.text]
                line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                if((choice == 2) or (choice == 4)):
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
        elif((bookStep == 6) or (bookStep == 12)):
            if(("1-自強號" in event.message.text) or ("2-莒光號" in event.message.text)):
                if(bookStep == 6):
                    information['goingType'] = event.message.text
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                    bookStep = 7
                else:
                    information['backType'] = event.message.text
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                    bookStep = 13
            else:
                line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(bookStep-1)))
        elif((bookStep == 7) or (bookStep == 13)):
            if startHourDict.__contains__(event.message.text):
                if(bookStep == 7):
                    information['goingStartHour'] = startHourDict[event.message.text]
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                    bookStep = 9
                else:
                    information["backStartHour"] = startHourDict[event.message.text]
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                    bookStep = 14
            else:
                line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(bookStep-1)))
        elif(bookStep == 8):
            if station.__contains__(event.message.text):
                information['endStation'] = station[event.message.text]
                line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                bookStep = 9
            else:
                line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=4))
        elif((bookStep == 9) or (bookStep == 14)):
            if((choice == 2) or (choice == 4)):
                if (endHourDict.__contains__(event.message.text)):
                    if((bookStep == 9) and (endHourDict[event.message.text] != information['goingStartHour'])):
                        information['goingEndHour'] = endHourDict[event.message.text]
                        line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                        bookStep = 10
                    elif((bookStep == 14) and (endHourDict[event.message.text] != information['backStartHour'])):
                        information['backEndHour'] =  endHourDict[event.message.text]
                        line_bot_api.reply_message(event.reply_token,ReplyMessage.confrimBook(infromation=information,choice=choice))
                        bookStep = 15
                    else:
                        line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=7))    
                else:
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=7))

            else:
                if(bookStep == 9):
                    information['goingTrain'] = event.message.text
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                    bookStep = 10
                else:
                    information['backTrain'] = event.message.text
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.confrimBook(infromation=information,choice=choice))
                    bookStep = 15

        elif(bookStep == 10):
            if checkData.checkTicketsNumbers(int(event.message.text)):
                information['goingticketNumbers'] = event.message.text
                if((choice==1) or (choice==2)):
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.confrimBook(infromation=information,choice=choice))
                    bookStep = 15
                else:
                    line_bot_api.reply_message(event.reply_token,ReplyMessage.bookTicketsMessage(step=bookStep))
                    bookStep = 11
            else:
                line_bot_api.reply_message(event.reply_token,ReplyMessage.errorMessage(step=(bookStep-1)))
        #If checke is not error, program automatically distinguish booking-date whether can book.
        #If it can book then book, store to database.
        elif(bookStep == 15):
            if "確認無誤" in event.message.text:
                information['id'] = ConnectDatabase.returnIdentification(information['id'])
                if ((choice == 1) or (choice == 2)):
                    if bookDate.__contains__(information['startDate']):
                        information['startDate'] = bookDate[information['startDate']]
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='馬上幫您訂票'))
                    else:
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='預約訂票'))
                        if choice == 1:
                            information['resver'] = 1
                        else:
                            information['resver'] = 2
                        ConnectDatabase.insertOneWayData(data=information)
                else:
                    if (bookDate.__contains__(information['startDate']) and bookDate.__contains__(information['endDate'])):
                        information['startDate'] = bookDate[information['startDate']]
                        information['endDate'] = bookDate[information['endDate']]
                        going,back =  breakUpReturnData(information=information,choice=choice,Reserve=True)

                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='馬上幫您訂票'))
                    elif bookDate.__contains__(information['startDate']):
                        information['startDate'] = bookDate[information['startDate']]
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='回程預約訂票'))
                        
                        backup = backupInfromation(information,choice=choice)
                       
                        ConnectDatabase.insertOneWayData(data=backup)
                    else:
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='都實施預約訂票'))
                        going,back =  breakUpReturnData(information=information,choice=choice,Reserve=True)
                        ConnectDatabase.insertOneWayData(data=going)
                        ConnectDatabase.insertOneWayData(data=back)

                bookStep = 0
                choice = 0
                information.clear()
            else:
                bookStep = 1

    
def updateDate(today):

    global station,bookDate,startHourDict,endHourDict,restart
    update = time.strftime("%Y%m%d",time.localtime())
    if ((update != today) or (restart == 0)):
        today = update
        restart = 1
        bookDate, station, startHourDict, endHourDict= BookTickets.BookDateAndStationData()


def backupInfromation(information, choice):
    backup = {}
    backup['startDate'] = information['endDate']
    backup['id'] = information['id']
    backup['goingticketNumbers'] = information['goingticketNumbers']
    backup['startStation'] = information['endStation']
    backup['endStation'] = information['startStation']
    if choice == 3:
        backup['goingTrain'] = information['backTrain']
        backup['resver'] = 1
    else:
        backup['goingType'] = infromation['backType']
        backup['goingStartHour'] = information['backStartHour']
        backup['goingEndHour'] = information['backEndHour']
        backup['resver'] = 2

    return backup

def breakUpReturnData(information,choice,Reserve=False):
    
    goInfor = {}
    backInfor = {}

    goInfor['id'] = information['id']
    goInfor['startDate'] = information['startDate']
    goInfor['goingticketNumbers'] = information['goingticketNumbers']
    goInfor['startStation'] = information['startStation']
    goInfor['endStation'] = information['endStation']

    backInfor['id'] = information['id']
    backInfor['startDate'] = information['endDate']
    backInfor['goingticketNumbers'] = information['goingticketNumbers']
    backInfor['startStation'] = information['endStation']
    backInfor['endStation'] = information['startStation']

    if choice == 3:
        goInfor['goingTrain'] = information['goingTrain']
        backInfor['goingTrain'] = information['backTrain']
    else:
        goInfor['goingType'] = information['goingType']
        goInfor['goingStartHour'] = information['goingStartHour']
        goInfor['goingEndHour'] = information['goingEndHour']

        backInfor['goingType'] = information['backType']
        backInfor['goingStartHour'] = information['backStartHour']
        backInfor['goingEndHour'] = information['backEndHour']

    if Reserve:
        goInfor['resver'] = int(choice/2)
        backInfor['resver'] = int(choice/2)
    return goInfor,backInfor
        


if  __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=5000)
