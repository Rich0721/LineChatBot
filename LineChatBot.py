'''************************************************
Autor: Rich
Version: 2
Date: 2018/08/27
Describe: Line chat-bot run. Reply question and check
data is true or not. And then help user book thickets.
Now, only book one-way thickets at train numbers.
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
import checkData
import BookOneWay

# Creating Flask object
app = Flask(__name__)


line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

global station,bookDate,startHourDict,endHourDict
station = {} # Train station data
bookDate = {} # Can book date
startHourDict = {}
endHourDict = {}
oneWayStep = 0  # Book one way tickets.


# Need user's data
global identificationNumber,startStation,endStation,startDate,endDate
global choice_train,thicketsNumber,trainNumber,startHour,endHour,train_type
identificationNumber = ''
startStation = ''
endStation = ''
startDate = ''
endDate = ''
thicketsNumber = 0
trainNumber =''
startHour = ''
endHour = ''

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
    global oneWayStep  # Book one way tickets.
    global identificationNumber
    global startStation
    global endStation
    global startDate
    global startHour,endHour
    global thicketsNumber
    global trainNumber,train_type
    global choice_train

    if ((event.message.text  == "Hi") or event.message.text == "你好"):
        line_bot_api.reply_message(event.reply_token, GreetingsMessage(step=1))
    if (("訂票" in event.message.text ) or ("訂車票" in event.message.text)):
        oneWayStep = 0
        line_bot_api.reply_message(event.reply_token, GreetingsMessage(step=2))
    

    if (("車次" in event.message.text)):
        choice_train = 1
        line_bot_api.reply_message(event.reply_token, GreetingsMessage(step=3))
    elif ('車種' in event.message.text):
        choice_train = 2
        line_bot_api.reply_message(event.reply_token, GreetingsMessage(step=3))


    #This is book one-way-tickets at train numbers'

    if ("單程票" in event.message.text):
        oneWayStep = 1
        line_bot_api.reply_message(event.reply_token, setOneWayTextMessege(step=oneWayStep))
    elif((oneWayStep >=1) and (oneWayStep <= 9)):
        if (oneWayStep == 1):
            if checkData.checkDate(date=event.message.text,dateDict=bookDate):
                oneWayStep = 2
                startDate = bookDate[event.message.text]
                line_bot_api.reply_message(event.reply_token, setOneWayTextMessege(step=oneWayStep))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="搭乘日期錯誤，請重新輸入"))
                oneWayStep = 1
        elif(oneWayStep == 2):
            if checkData.checkIdentificationNumber(event.message.text):
                identificationNumber = event.message.text
                if(choice_train==1):
                    oneWayStep = 3 
                    line_bot_api.reply_message(event.reply_token, setOneWayTextMessege(step=oneWayStep))
                else:
                    oneWayStep = 4
                    line_bot_api.reply_message(event.reply_token, setOneWayTextMessege(step=oneWayStep))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="身份證字號錯誤，請重新輸入"))
                oneWayStep = 2
        elif (oneWayStep == 3):
            oneWayStep = 4
            trainNumber = event.message.text
            line_bot_api.reply_message(event.reply_token, setOneWayTextMessege(step=oneWayStep))
        elif (oneWayStep == 4):
            if checkData.checkStation(event.message.text,station):
                oneWayStep = 5
                startStation = station[event.message.text]
                line_bot_api.reply_message(event.reply_token, setOneWayTextMessege(step=oneWayStep))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="起站別錯誤，請檢查名稱是否有錯字"))
                oneWayStep = 4
        elif (oneWayStep == 5):
            if ((checkData.checkStation(event.message.text,station)) and (event.message.text != startStation)):
                oneWayStep = 6
                endStation = station[event.message.text]
                line_bot_api.reply_message(event.reply_token, setOneWayTextMessege(step=oneWayStep))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="訖站別錯誤，請檢查名稱是否有錯字"))
                oneWayStep = 5
        elif (oneWayStep == 6):
            if checkData.checkTicketsNumbers(int(event.message.text)):
                thicketsNumber = event.message.text
                if (choice_train == 1):
                    oneWayStep = 0
                    line_bot_api.reply_message(event.reply_token,confrimBook(step=1))
                else:
                    oneWayStep = 7
                    line_bot_api.reply_message(event.reply_token,setOneWayTextMessege(oneWayStep))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="每次訂票的數量至多六張喔~"))
        elif (oneWayStep == 7):
            if checkData.checkHour(event.message.text, startHourDict):
                oneWayStep = 8
                startHour = event.message.text
                line_bot_api.reply_message(event.reply_token, setOneWayTextMessege(oneWayStep))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='''時間格式錯誤或沒有以小時為單位 EX:0900'''))
        elif (oneWayStep == 8):
            if ((checkData.checkHour(event.message.text,endHourDict)) and (startHour < event.message.text)):
                oneWayStep = 9
                startHour = startHourDict[startHour]
                endHour = endHourDict[event.message.text]
                line_bot_api.reply_message(event.reply_token,setOneWayTextMessege(oneWayStep))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='''時間格式錯誤或沒有以小時為單位 EX:0900'''))
        elif(oneWayStep == 9):
            if((event.message.text == "1-自強號") or (event.message.text == "2-莒光號")):
                oneWayStep = 0
                train_type = event.message.text
                line_bot_api.reply_message(event.reply_token,confrimBook(step=2))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="請按選單!!"))
    elif(("Booking" in event.message.text) and (oneWayStep == 0)):
        if(choice_train == 1):# Booking train number
            success = BookOneWay.bookOneWay(person_id=identificationNumber,date=startDate,train_no=trainNumber,
                startStation=startStation,toStation=endStation,ticketNumber=thicketsNumber)
        else:
            success = BookOneWay.bookOneWay(person_id=identificationNumber,date=startDate,train_kind=train_type,
                startStation=startStation,toStation=endStation,ticketNumber=thicketsNumber)

        if(success):
            line_bot_api.reply_message(event.reply_token,ImageSendMessage())
        revertData()
    elif("重新輸入" in event.message.text):
        oneWayStep = 1
        line_bot_api.reply_message(event.reply_token,setOneWayTextMessege(oneWayStep))

    
def updateDate(today):

    global station,bookDate,startHourDict,endHourDict,restart
    update = time.strftime("%Y%m%d",time.localtime())
    if ((update != today) or (restart == 0)):
        today = update
        restart = 1
        bookDate, station, startHourDict, endHourDict= BookOneWay.BookDateAndStationData()


def GreetingsMessage(step=0):
    
    if step == 1:
        message = TextSendMessage(text="你好，我是台鐵訂票機器人，並不是官方機器人，如害怕個資洩漏，請至台鐵官網自行訂票")
    elif step == 2:
        message =TemplateSendMessage(
            alt_text = "Confirm template",
            template= ConfirmTemplate(
                text="請選擇想要訂票的方式",
            actions=[
                PostbackTemplateAction(
                    label='車次',
                    text='車次',
                    data='action=buy&itemid=1'),
                MessageTemplateAction(
                    label='車種',
                    text='車種')
                ]))
    elif step == 3:
        message =TemplateSendMessage(
            alt_text = "Confirm template",
            template= ConfirmTemplate(
                text="請選擇想要訂票的方式",
            actions=[
                PostbackTemplateAction(
                    label='單程票',
                    text='單程票',
                    data='action=buy&itemid=1'),
                MessageTemplateAction(
                    label='來回票',
                    text='來回票')
                ]))
    return message


def setOneWayTextMessege(step=0):
    if step == 1:
        message = TextSendMessage(text='''現在開始幫忙您訂單程票，請告知我你想要乘車的日期，
                請按照格式輸入 EX:2018/09/11''')
    elif step == 2:
        message = TextSendMessage(text='''請告知我您的身份證字號，請按照格式輸入 EX:A123456789''')
    elif step == 3:
        message = TextSendMessage(text='''請告知我您欲搭乘的車次代碼，請按照格式輸入 EX:122''')
    elif step == 4:
        message = TextSendMessage(text='''請告知我您的起站 EX:台北''')
    elif step == 5:
        message = TextSendMessage(text='''請告知我您的訖站 EX:台北''')
    elif step == 6:
        message = TextSendMessage(text='''請告知您的訂票數 EX:1 (如超過6張票以上，請分兩次訂票)''')
    elif step == 7:
        message = TextMessage(text='''欲搭乘時間範圍的開始時間，請以整點為單位 EX:0900''')
    elif step == 8 :
        message = TextMessage(text='''欲搭乘時間範圍的結束時間，請以整點為單位，最晚時間到23:59 EX:0900''')
    elif step == 9 :
        message = TemplateSendMessage(
            alt_text = "車種確認",
            template = ConfirmTemplate(
                text = "請確認預定車種",
                actions = [
                    PostbackTemplateAction(
                        label="1-自強號",
                        text="1-自強號",
                        data='action=buy&itemid=1'),
                    MessageTemplateAction(
                        label="2-莒光號",
                        text="2-莒光號")
                ]
                )
            )
    return message

def confrimBook(step=0):
    if(step == 1):
        message =TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text='''請確認輸入資料是否有誤
            身份證:{}
            乘車日期:{}
            車次代碼:{}
            起站:{}
            訖站:{}
            票數:{}'''.format(identificationNumber,startDate,trainNumber,startStation,
                    endStation,thicketsNumber),
                actions=[
                    PostbackTemplateAction(
                        label='開始訂票',
                        text='Booking',
                        data='action=buy&itemid=1'
                    ),
                    MessageTemplateAction(
                        label='重新輸入',
                        text='重新輸入'
                    )
                ]
            )
        )
    elif(step == 2):
        message =TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text='''請確認輸入資料是否有誤
            身份證:{}
            乘車日期:{}
            起站:{}
            訖站:{}
            車種:{}
            起始時間:{}
            截止時間:{}
            票數:{}'''.format(identificationNumber,startDate,startStation,endStation,
                train_type,startHour,endHour,thicketsNumber),
                actions=[
                    PostbackTemplateAction(
                        label='開始訂票',
                        text='Booking',
                        data='action=buy&itemid=1'
                    ),
                    MessageTemplateAction(
                        label='重新輸入',
                        text='重新輸入'
                    )
                ]
            )
        )
    return message

def revertData():
    global identificationNumber,startStation,endStation,startDate,endDate,train_type
    global choice_train,thicketsNumber,trainNumber,startHour,endHour,choice_train
    identificationNumber = ''
    startStation = ''
    endStation = ''
    startDate = ''
    endDate = ''
    thicketsNumber = 0
    trainNumber =''
    startHour = ''
    endHour = ''
    train_type =''
    choice_train = 0




if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)
