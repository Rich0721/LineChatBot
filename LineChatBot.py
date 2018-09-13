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
import checkData,BookTickets,ReplyMessage,ConnectDatabase

# Creating Flask object
app = Flask(__name__)



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
    "goingType":"",
    "backType":"",
    "startStation":"",
    "endStation":"",
    "ticketNumbers":""
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

    if ((event.message.text  == "Hi") or (event.message.text == "你好")):
        line_bot_api.reply_message(event.reply_token, ReplyMessage.GreetingsMessage(step=2))
        registedStep = 1
        bookStep = 1
    elif("已註冊" in event.message.text):
        line_bot_api.reply_message(event.reply_token, ReplyMessage.GreetingsMessage(step=3))
    #else:
    #    line_bot_api.reply_message(event.reply_token, ReplyMessage.GreetingsMessage(step=1))

    if("未註冊" in event.message.text):
        line_bot_api.reply_message(event.reply_token,ReplyMessage.registerMessage(registedstep=1))
        registedStep = 2
    elif("單程-車次" in event.message.text):
        choice = 1
    elif("單程-車種" in event.message.text):
        choice = 2
    elif("來回-車次" in event.message.text):
        choice = 3
    elif("來回-車種" in event.message.text):
        choice = 4

        
    if(registedStep == 2):
        registedDict['id'] = event.message.text
        line_bot_api.reply_message(event.reply_token,ReplyMessage.registerMessage(registedstep=registedStep))
        registedStep = 3
    elif registedStep == 3:
        registedDict['userName'] = event.message.text
        if ConnectDatabase.register(registedDict):
            line_bot_api.reply_message(event.reply_token,ReplyMessage.registerMessage(registedstep=registedStep))
            registedStep = 0
            registedDict.clear()
        else:
            line_bot_api.reply_message(event.reply_token,ReplyMessage.registerMessage(registedstep=4))



    
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
