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
        message = TextSendMessage(text="你好，我是台鐵訂票機器人，並不是官方機器人，如害怕個資洩漏，請至台鐵官網自行訂票，\
            請輸入 「Hi」或「你好」，將會提供你工作選項")
    elif step == 2:
        message =TemplateSendMessage(
            alt_text = "工作選項",
            template= ButtonsTemplate(
                text="請選擇想要的目的",
            actions=[
                MessageTemplateAction(
                    label='訂票去',
                    text='訂票去',),
                MessageTemplateAction(
                    label='未註冊',
                    text='未註冊'),
                MessageTemplateAction(
                    label='查詢訂票',
                    text='查詢訂票')
                ]))
    elif step == 3:
        message =TemplateSendMessage(
            alt_text = "訂票方式",
            template= ButtonsTemplate(
                text="請選擇想要的訂票方式",
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

def registerMessage(registedstep=0):
    if registedstep == 1:
        message = TextSendMessage(text="請告知我您的身份證字號")
    elif registedstep == 2:
        message = TextSendMessage(text='請輸入使用者名稱')
    elif registedstep == 3:
        message = TextSendMessage(text="註冊成功")
    elif registedstep == 4:
        message = TextSendMessage(text="id已存在，請重新輸入使用者名稱")

    return message


'''********************************************
Step's significance
1:ID. 
2:Going date.
3:Start staition.
4:Destination station.
5:Going Train type.
6:Going date's start hour.
7:Going date's end hour.
8:Going Train number.
9:Going Ticket's numbers.

If user book return tickets.
10:Back date.
11:Back Train type.
12:Back date's start hour.
13:Back date's end hour.
14:Back Train number.

********************************************'''


def bookTicketsMessage(step=0):
    if step == 1:
        message = TextSendMessage(text='''請告知我您註冊的使用者名稱''')
    elif step == 2:
        message = TextSendMessage(text='''請告知我去程乘車的日期，請按照格式輸入 EX:2018/09/11''')
    elif step == 3:
        message = TextSendMessage(text='''請告知我您的起站 EX:台北''')
    elif step == 4:
        message = TextSendMessage(text='''請告知我您的訖站 EX:台北''')
    elif ((step == 5) or (step==11)) :
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
    elif((step == 6) or (step == 12)):
        message = TextMessage(text='''欲搭乘時間範圍的開始時間，請以整點為單位 EX:0900''')
    elif((step == 7) or (step == 13)) :
        message = TextMessage(text='''欲搭乘時間範圍的結束時間，請以整點為單位，最晚時間到23:59 EX:0900''')    
    elif ((step == 8) or (step == 14)):
        message = TextSendMessage(text='''請告知我您欲搭乘的車次代碼，請按照格式輸入 EX:122''')
    elif (step == 9):
        message = TextSendMessage(text='''請告知您的訂票數 EX:1 (如超過6張票以上，請分兩次訂票)，如果是預定來回票，票數會自動購買相同數量。''')
    elif step == 10:
        message = TextSendMessage(text='''請告知我回程乘車的日期，請按照格式輸入 EX:2018/09/11''')
    
    
    
    
    return message

def errorMessage(step=0):  
    if(step == 1):
        message = TextSendMessage(text="使用者名稱錯誤，請重新輸入")
    elif(step == 2):
        message = TextSendMessage(text="去程日期錯誤，請重新輸入")
    elif(step == 3):
        message = TextSendMessage(text="起站別錯誤，請檢查名稱是否有錯字")
    elif(step == 4):
        message = TextSendMessage(text="訖站別錯誤，請檢查名稱是否有錯字")
    elif((step == 5) or (step == 11)):
        message = TextSendMessage(text="請按選擇鈕!")
    elif(step == 6):
        message = TextSendMessage(text="去程起始時間錯誤，請重新輸入")
    elif(step == 7):
        message = TextSendMessage(text="去程截止時間錯誤，請重新輸入")
    elif((step == 9) or (step == 15)):
        message = TextSendMessage(text="每次訂票的數量至多六張喔~")
    elif(step == 10):
        message = TextSendMessage(text="回程日期錯誤，請重新輸入")
    elif(step == 12):
        message = TextSendMessage(text="回程起始時間錯誤，請重新輸入")
    elif(step == 13):
        message = TextSendMessage(text="回程截止時間錯誤，請重新輸入")
    return message


'''********************************************
Step's significance
1:Book one-way tickets when use train numbers.
2:Book one-way tickets when use train type.
3:Book return tickets when use train numbers.
4:Book return tickets when use train type.
5:Confrim register's data whether correct.
********************************************'''

def confrimBook(infromation,choice=0):
    if(choice == 1):
        message =TemplateSendMessage(
            alt_text='車次單程票確認',
            template=ConfirmTemplate(
                text='''請確認輸入資料是否有誤
            ID:{}
            --------------
            乘車日期:{}
            車次代碼:{}
            --------------
            {}→{}
            票數:{}'''.format(infromation["id"],infromation["startDate"],infromation["goingTrain"],
            	infromation["startStation"],infromation["endStation"],infromation["goingticketNumbers"]),
                actions=[
                    PostbackTemplateAction(
                        label='確認無誤',
                        text='確認無誤',
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
                text='''ID:{}
            乘車日期:{}
            起始時間:{}
            截止時間:{}
            車種:{}
            {}→{}
            票數:{}'''.format(infromation['id'],infromation['startDate'],infromation['goingStartHour'],
                    infromation['goingEndHour'],infromation['goingType'],infromation['startStation'],infromation['endStation'],
                    infromation['goingticketNumbers']),
                actions=[
                    PostbackTemplateAction(
                        label='確認無誤',
                        text='確認無誤',
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
                text='''
                ID:{}
                {}
                車次代碼:{}
                {}
                車次代碼:{}
                票數:{}
                {}→{}
                '''.format(infromation['id'],infromation['startDate'],infromation['goingTrain'],
                    infromation['endDate'],infromation['backTrain'],infromation['goingticketNumbers'],
                    infromation['startStation'],infromation['endStation']),
                actions=[
                    MessageTemplateAction(
                        label="確認無誤",
                        text="確認無誤"),
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
            ID:{}
            {}
            去程起始時間:{}
            去程截止時間:{}
            去程車種:{}
            {}
            回程起始時間:{}
            回程截止時間:{}
            回程車種:{}
            票數:{}
            {}→{}'''.format(infromation['id'],infromation['startDate'],infromation['goingStartHour'],
                    infromation['goingEndHour'],infromation['goingTrain'],
                    infromation['endDate'],infromation['backStartHour'],
                    infromation['backEndHour'],infromation['backTrain'],infromation['goingticketNumbers'],
                    infromation['startStation'],infromation['endStation']),
                actions=[
                    PostbackTemplateAction(
                        label='確認無誤',
                        text='確認無誤',
                        data='action=buy&itemid=1'
                    ),
                    MessageTemplateAction(
                        label='重新輸入',
                        text='重新輸入'
                    )
                ]
            )
        )
    elif(choice == 5):
        message = TemplateSendMessage(
            alt_text="註冊訊息確認",
            template=ConfirmTemplate(
                text = '''請確認輸入註冊資料
                身份證:{}
                使用者名稱:{}'''.format(infromation['id'],infromation['userName']),
                actions=[
                    PostbackTemplateAction(
                        label="確認無誤",
                        text="確認無誤",
                        data='action=buy&itemid=1'),
                    MessageTemplateAction(
                        label='輸入錯誤',
                        text="輸入錯誤")
                ]
                )
            )
    else:
        message = TemplateSendMessage(
            alt_text='立即訂票或預約訂票',
            template=ConfirmTemplate(
                text="立即訂票或預約訂票",
                actions=[
                PostbackTemplateAction(
                    label="立即訂票",
                    text="立即訂票",
                    data='action=buy&itemid=1'),
                MessageTemplateAction(
                    label="預約訂票",
                    text="預約訂票")
                ]
                )
            )

    return message