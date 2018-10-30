'''******************************************************
Author: Rich
Version: 1
First_Date: 2018/09/13
Describe: Connect myself mangoDB store users' data that 
	are protected.
*********************************************************'''

from pymongo import MongoClient
from bson.objectid import ObjectId

#connection
db = conn.booktrain
person_table = db.person
oneway_table = db.oneway
reserve_table = db.reserve

def register(data):
	person_table.insert_one(data)

def confirmeID(data):
	id_exist = person_table.find_one({'id':data})
	if id_exist == None:
		return True
	return False

def confirmeUserName(data):
	id_exist = person_table.find_one({'userName':data})
	if id_exist == None:
		return True
	return False


def searchID(data):
	id_exist = person_table.find_one({'userName':data})
	if id_exist != None:
		return True
	return False


def returnIdentification(data):
	id = person_table.find_one({'userName':data})
	return id['id']

def returnUserName(data):
	userName = person_table.find_one({'id':data})
	return userName['userName']

def insertOneWayData(data):
	oneway_table.insert(data)

def searchOneWayData(data):
	if oneway_table.find_one({'startDate':data}):
		return(oneway_table.find_one_and_delete({'startDate': data}))

def ReserveData(data,store=False,delete=False):
	if store:
		reserve_table.insert_one(data)
	elif delete:
		reserve_table.delete_many({"pick_up_deadling":data})

def searchReserveData(data):
	return reserve_table.find_one({'userName':data})

