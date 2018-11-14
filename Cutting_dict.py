def cutRegisted(information):
	Registed = {}
	Registed['id'] = information['id']
	Registed['userName'] = information['userName']
	return Registed


# If back date need to resver, return data  need to back up then store. 
def backupInfromation(information, choice):
    backup = {}
    backup['startDate'] = information['endDate']
    backup['id'] = information['id']
    backup['goingticketNumbers'] = information['goingticketNumbers']
    backup['startStation'] = information['endStation']
    backup['endStation'] = information['startStation']
    if choice == 3:
        backup['goingTrain'] = information['backTrain']
        backup['reserve'] = 1
    else:
        backup['goingType'] = infromation['backType']
        backup['goingStartHour'] = information['backStartHour']
        backup['goingEndHour'] = information['backEndHour']
        backup['reserve'] = 2

    return backup

# Break up data to one-way formal.
def breakUpReturnData(information,choice):
    
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

    
    goInfor['reserve'] = int(choice/2)
    backInfor['reserve'] = int(choice/2)
    return goInfor,backInfor