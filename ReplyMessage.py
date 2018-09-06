'''************************************************
Autor: Rich
Version: 1
Date: 2018/09/03
Describe: Line chat-bot reply message.
************************************************'''
from linebot.models import(
	MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,
    TemplateSendMessage, ConfirmTemplate,PostbackTemplateAction,MessageTemplateAction,
    ButtonsTemplate
)

def GreetingsMessage(step=0):
    
    if step == 1:
        message = TextSendMessage(text="你好，我是台鐵訂票機器人，並不是官方機器人，如害怕個資洩漏，請至台鐵官網自行訂票")
    elif step == 2:
        message =TemplateSendMessage(
            alt_text = "訂票方式",
            template= ButtonsTemplate(
                text="請選擇想要訂票的方式",
            actions=[
                MessageTemplateAction(
                    label='單程-車次',
                    text='單程-車次',),
                MessageTemplateAction(
                    label='單程-車種',
                    text='單程-車種'),
                MessageTemplateAction(
                    label='來回-車次',
                    text='來回-車次'),
                MessageTemplateAction(
                    label='來回-車種',
                    text='來回-車種')
                ]))
    return message


'''********************************************
Step's significance
1:ID. 
2:Going date.
3:Back date.
4:Going date's start hour.
5:Going date's end hour.
6:Back date's start hour.
7:Back date's end hour.
8:Train number.
9:Train type.
10:Start staition.
11:Destination station.
12:Tickets.
********************************************'''


def bookTicketsMessege(step=0):
    if step == 1:
        message = TextSendMessage(text='''請告知我您的身份證字號，請按照格式輸入 EX:A123456789''')
    elif step == 2:
        message = TextSendMessage(text='''請告知我去程乘車的日期，請按照格式輸入 EX:2018/09/11''')
    elif step == 3:
        message = TextSendMessage(text='''請告知我回程乘車的日期，請按照格式輸入 EX:2018/09/11''')
    elif((step == 4) or (step == 6)):
        message = TextMessage(text='''欲搭乘時間範圍的開始時間，請以整點為單位 EX:0900''')
    elif((step == 5) or (step == 7)) :
        message = TextMessage(text='''欲搭乘時間範圍的結束時間，請以整點為單位，最晚時間到23:59 EX:0900''')    
    elif step == 8:
        message = TextSendMessage(text='''請告知我您欲搭乘的車次代碼，請按照格式輸入 EX:122''')
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
    elif step == 10:
        message = TextSendMessage(text='''請告知我您的起站 EX:台北''')
    elif step == 11:
        message = TextSendMessage(text='''請告知我您的訖站 EX:台北''')
    elif step == 12:
        message = TextSendMessage(text='''請告知您的訂票數 EX:1 (如超過6張票以上，請分兩次訂票)''')
    
    
    return message

def errorMesserge(step=0):
	if(step == 1):
		message = TextSendMessage(text="身份證字號錯誤，請重新輸入")
	elif(step == 2):
		message = TextSendMessage(text="去程日期錯誤，請重新輸入")
	elif(step == 3):
		message = TextSendMessage(text="回程日期錯誤，請重新輸入")
	elif(step == 4):
		message = TextSendMessage(text="去程起始時間錯誤，請重新輸入")
	elif(step == 5):
		message = TextSendMessage(text="去程截止時間錯誤，請重新輸入")
	elif(step == 6):
		message = TextSendMessage(text="回程起始時間錯誤，請重新輸入")
	elif(step == 7):
		message = TextSendMessage(text="回程截止時間錯誤，請重新輸入")
	elif(step == 9):
		message = TextSendMessage(text="請按選擇鈕!")
	elif(step == 10):
		message = TextSendMessage(text="起站別錯誤，請檢查名稱是否有錯字")
	elif(step == 11):
		message = TextSendMessage(text="訖站別錯誤，請檢查名稱是否有錯字")
	elif(step == 12):
		message =  TextSendMessage(text="每次訂票的數量至多六張喔~")
	

	return message


'''********************************************
Step's significance
1:Book one-way tickets when use train numbers.
2:Book one-way tickets when use train type.
3:Book return tickets when use train numbers.
4:Book return tickets when use train type.
********************************************'''

def confrimBook(infromation,choice=0):
    if(choice == 1):
        message =TemplateSendMessage(
            alt_text='車次單程票確認',
            template=ConfirmTemplate(
                text='''請確認輸入資料是否有誤
            身份證:{}
            --------------
            乘車日期:{}
            車次代碼:{}
            --------------
            {}→{}
            票數:{}'''.format(infromation["id"],infromation["startDate"],infromation["goingTrain"],
            	infromation["startStation"],infromation["endStation"],infromation["thicketNumbers"]),
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
    elif(choice == 2):
        message =TemplateSendMessage(
            alt_text='車種單程票確認',
            template=ConfirmTemplate(
                text='''請確認輸入資料是否有誤
            身份證:{}
            --------------
            乘車日期:{}
            起始時間:{}
            截止時間:{}
            車種:{}
            --------------
            {}→{}
            票數:{}'''.format(infromation['id'],infromation['startDate'],infromation['goingStartHour'],
                    infromation['goingEndHour'],infromation['goingType'],infromation['startStation'],infromation['endStation'],
                    infromation['thicketNumbers']),
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
    elif(choice == 3):
        message = TemplateSendMessage(
            alt_text="車次來回票確認",
            template=ConfirmTemplate(
                text='''請確認輸入資料是否有誤
                身份證:{}
                --------------
                去程日期:{}
                車次代碼:{}
                --------------
                回程日期:{}
                車次代碼:{}
                --------------
                {}→{}
                票數:{}'''.format(infromation['id'],infromation['startDate'],infromation['goingTrain'],
                    infromation['endDate'],infromation['backTrain'],infromation['startStation'],infromation['endStation'],
                    infromation['thicketNumbers']),
                actions=[
                    MessageTemplateAction(
                        label="開始訂票",
                        text="Booking"),
                    MessageTemplateAction(
                        label='重新輸入',
                        text='重新輸入')
                    ]
                )
            )
    elif(choice == 4):
        message =TemplateSendMessage(
            alt_text='車種來回票確認',
            template=ConfirmTemplate(
                text='''請確認輸入資料是否有誤
            身份證:{}
            ---------------
            去程日期:{}
            去程起始時間:{}
            去程截止時間:{}
            去程車種:{}
            ---------------
            回程日期:{}
            回程起始時間:{}
            回程截止時間:{}
            回程車種:{}
            ---------------
            {}→{}
            票數:{}'''.format(infromation['id'],infromation['startDate'],infromation['goingStartHour'],
                    infromation['goingEndHour'],infromation['goingType'],infromation['endDate'],infromation['backStartHour'],
                    infromation['backEndHour'],infromation['backType'],infromation['startStation'],infromation['endStation'],
                    infromation['thicketNumbers']),
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