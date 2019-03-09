from pymongo import MongoClient
from manifest import NAVIGATOR_KEY_LIST
from fuzzywuzzy import fuzz

conn = MongoClient('localhost',27017)
db = conn.trident_signature
login_data = db.login_data
user_data = db.user_data

distance_string_list = []

for document in login_data.find():
	distance_string = ""
	for key in NAVIGATOR_KEY_LIST:
		distance_string += str(document.get("navigator",{}).get(key,""))+"|"
	for element in distance_string_list:
		print "ratio",fuzz.ratio(element,distance_string)
	distance_string_list.append(distance_string)
	print "\n\n"
	# print "<<<",distance_string,">>>"


