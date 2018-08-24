'''************************************************
Autor: Rich
Version: 1
Date: 2018/08/24
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

#Token
CHANNEL_ACCESS_TOKEN = ""
CHANNEL_SECRET = ""

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

global station,bookDate
station = {} # Train station data
bookDate = {} # Can book date
oneWayStep = 0  # Book one way tickets.

global choice_train

# Need user's data
global identificationNumber
identificationNumber = ''
global startStation
startStation = ''
global endStation
endStation = ''
global startDate
startDate = ''
global endDate
endDate = ''
global thicketsNumber
thicketsNumber = 0
global trainNumber
trainNumber =''

# Book date update.
global today,restart
today = time.strftime("%Y%m%d",time.localtime())
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

def updateDate():
    global station,bookDate,restart,today
    update = time.strftime("%Y%m%d",time.localtime())
    if ((update != today) or (restart == 0)):
        today = update
        restart = 1
        bookDate, station = BookOneWay.BookDateAndStationData()

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    updateDate()
    global oneWayStep  # Book one way tickets.
    global identificationNumber
    global startStation
    global endStation
    global startDate
    global endDate
    global thicketsNumber
    global trainNumber
    global choice_train

    if ((event.message.text  == "Hi") or event.message.text == "你好"):
        line_bot_api.reply_message(event.reply_token, GreetingsMessage(step=1))
        choice = 0
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

    if (("單程票" in event.message.text) and (choice_train == 1)):
        oneWayStep = 1
        line_bot_api.reply_message(event.reply_token, setOneWayTextMessege(step=oneWayStep))
    elif((oneWayStep >=1) and (oneWayStep < 7)):
        if (oneWayStep == 1):
            if checkData.checkDate(date=event.message.text,dateDict=bookDate):
                oneWayStep = 2
                startDate = event.message.text
                line_bot_api.reply_message(event.reply_token, setOneWayTextMessege(step=oneWayStep))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="搭乘日期錯誤，請重新輸入"))
                oneWayStep = 1
        elif(oneWayStep == 2):
            if checkData.checkIdentificationNumber(event.message.text):
                oneWayStep = 3 
                identificationNumber = event.message.text
                line_bot_api.reply_message(event.reply_token, setOneWayTextMessege(step=oneWayStep))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="身份證字號錯誤，請重新輸入"))
                oneWayStep = 2
        elif (oneWayStep == 3):
            oneWayStep = 4
            trainNumber = int(event.message.text)
            line_bot_api.reply_message(event.reply_token, setOneWayTextMessege(step=oneWayStep))
        elif (oneWayStep == 4):
            if checkData.checkStation(event.message.text,station):
                oneWayStep = 5
                startStation = event.message.text
                line_bot_api.reply_message(event.reply_token, setOneWayTextMessege(step=oneWayStep))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="起站別錯誤，請檢查名稱是否有錯字"))
                oneWayStep = 4
        elif (oneWayStep == 5):
            if ((checkData.checkStation(event.message.text,station)) and (event.message.text != startStation)):
                oneWayStep = 6
                endStation = event.message.text
                line_bot_api.reply_message(event.reply_token, setOneWayTextMessege(step=oneWayStep))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="訖站別錯誤，請檢查名稱是否有錯字"))
                oneWayStep = 5
        elif (oneWayStep == 6):
            if checkData.checkTicketsNumbers(int(event.message.text)):
                oneWayStep = 0
                thicketsNumber = event.message.text
                line_bot_api.reply_message(event.reply_token, confrimBook())
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="每次訂票的數量至多六張喔~"))
    elif("確認無誤" in event.message.text):
        line_bot_api.reply_message(event.reply_token,TextMessage(text="馬上幫您訂票"))
    elif("輸入錯誤" in event.message.text):
        oneWayStep = 1
        line_bot_api.reply_message(event.reply_token,setOneWayTextMessege(oneWayStep))
    else:
        line_bot_api.reply_message(
        event.reply_token,
        confrimBook())
    
    


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
        message = TextSendMessage(text='''現在開始幫忙您訂車次單程票，請告知我你想要乘車的日期，
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
    return message

def confrimBook():

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
                    label='確認無誤',
                    text='確認無誤',
                    data='action=buy&itemid=1'
                ),
                 MessageTemplateAction(
                    label='輸入錯誤',
                    text='輸入錯誤'
                )
            ]
        )
    )

    return message

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port)
