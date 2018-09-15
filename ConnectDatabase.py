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
favorite_table = db.favorite

def register(data):
	person_table.insert_one(data)

def confirmeID(data):
	id_exist = person_table.find_one({'userName':data['userName']})
	if id_exist == None:
		return True
	return False

def searchID(data):
	id_exist = person_table.find_one({'userName':data})
	if id_exist != None:
		return True
	return False

def FavroiteExsit(data):
	exist = favorite_table.find_one(data)
	if exist != None:
		return True
	return False

def insertFavorite(data):
	favorite_table.insert_one(data)
