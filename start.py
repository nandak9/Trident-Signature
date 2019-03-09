from flask import Flask,render_template,make_response,request,jsonify,Response,redirect,send_from_directory
import time
import json
import os
from xlrd import open_workbook
from xlutils.copy import copy
import hashlib
import math
import numpy
import cluster
import datetime
import redis
from fuzzywuzzy import fuzz
from pymongo import MongoClient
from pymongo import DESCENDING

redis_conn = redis.Redis(host='localhost', port=6379,db=7)
conn = MongoClient('localhost',27017)
db = conn.trident_signature
login_data = db.login_data
user_data = db.user_data
acs_client_data = db.acs_client_data
transaction_data = db.transaction_data
app = Flask(__name__)

@app.route('/static/<path:path>')
def send_static(path):
	print "static_link",path
	return send_from_directory('static', path)

@app.route("/",methods=["POST","GET"])
def home():
	if request.method == "GET":
		return make_response(render_template('test.html',completed=False))
	if request.method == "POST":
		name = request.form.get("name","Shobhit")
		emp_id = request.form.get("emp_id","MYP1007")
		email = request.form.get("email","shobhit.verma@mypoolin.com")
		channel = request.form.get("channel","WEB")
		keyArray = json.loads(request.form.get("keyArray","{}"))
		mouseEvents = json.loads(request.form.get("mouseEvents","{}"))
		navigator = json.loads(request.form.get("navigator","navigator"))
		timestamp = str(int(time.time()))[:10]
		datetime_string = datetime.datetime.strftime(datetime.datetime.fromtimestamp(float(timestamp)),"%Y-%m-%d %H:%M:%S")
		json_present = 0
		print "request form is",request.form
		doc = login_data.find_one({"emp_id":emp_id})
		if doc:
			json_present = 1
		if json_present == 0:
			jso = {"name":name,
							"emp_id":emp_id,
							"status":"VERIFIED",
							"email":email,
							"keyArray":keyArray,
							"mouseEvents":mouseEvents,
							"navigator":navigator,
							"headers":dict(request.headers),
							"timestamp":timestamp,
							"datetime":datetime_string,
							"channel":channel
				}
			login_data.insert_one(jso)
			user_data.insert_one({"emp_id":emp_id,
								"email":email,
								"name":name,
								"device_strings":[cluster.return_device_id_string(jso,channel)]
							})
			# f = open("json_storage/"+emp_id+"|"+str(int(time.time()))[:10]+".json","w")
			# f.write(json.dumps())
			# f.close()
		else:
			login_data.insert_one({"name":name,
							"emp_id":emp_id,
							"status":"PENDING",
							"email":email,
							"keyArray":keyArray,
							"mouseEvents":mouseEvents,
							"navigator":navigator,
							"headers":dict(request.headers),
							"timestamp":timestamp,
							"datetime":datetime_string,
							"channel":channel
				})
			# f = open("json_storage/"+emp_id+"|"+str(int(time.time()))[:10]+".json","w")
			# f.write(json.dumps({"name":name,
			# 	"emp_id":emp_id,
			# 	"status":"PENDING",
			# 	"email":email,
			# 	"keyArray":keyArray,
			# 	"mouseEvents":mouseEvents,
			# 	"navigator":navigator,
			# 	"headers":dict(request.headers)
			# 	}))
			# f.close()
		# print "name=",name,"emp_id=",emp_id,"email=",email,"keyArray=",keyArray,"mouseEvents=",mouseEvents
		return make_response(render_template('test.html',completed=True))


@app.route('/initiation_call',methods=['POST'])
def initiation_call():
	posted_json = request.get_json()
	client_id = posted_json.get("client_id","MYP10101")
	hashed_card_number = posted_json.get("hashed_card_number","")
	user = acs_client_data.find_one({"hashed_card_number":hashed_card_number})
	del user["_id"]
	redis_conn.hmset(client_id,user)
	redis_conn.set(client_id+":hashed_card_number",hashed_card_number)
	# print client_id,hashed_card_number
	return jsonify({"status":"ok","message":"success"})


@app.route('/posting_data',methods=['POST'])
def posting_data():
	posted_json = request.get_json()
	client_id = posted_json.get("client_id")
	navigator = posted_json.get("navigator")
	timestamp = str(int(time.time()))[:10]
	datetime_string = datetime.datetime.strftime(datetime.datetime.fromtimestamp(float(timestamp)),"%Y-%m-%d %H:%M:%S")
	json_present = 0
	doc = redis_conn.hgetall(client_id)
	client_hashed_card_number = redis_conn.get(client_id+":hashed_card_number")
	jso = {
			"hashed_card_number":client_hashed_card_number,
			"status":"VERIFIED",
			"navigator":navigator,
			"headers":dict(request.headers),
			"timestamp":timestamp,
			"datetime":datetime_string
			}
	current_device_string = cluster.return_device_id_string(jso)
	transaction_data.insert_one(jso)
	push_device_flag = 1
	# user = acs_client_data.find_one({"hashed_card_number":hashed_card_number})
	# for device_string in user.get("device_strings",[]):
	# 	userAgent = device_string.split("|")[19]
	# 	device_match_percentage = cluster.return_fuzz_score_for_device(device_string,current_device_string)
	# 	device_hash = hashlib.sha512(device_string).hexdigest()
	# 	device_type = "Unidentified"
	# 	if device_match_percentage >= 95:
	# 		push_device_flag = 0
	# 	# print userAgent
	# 	if "Android" in device_string:
	# 		device_type = "Mobile Android"
	# 	elif "iPhone" in device_string:
	# 		device_type = "Mobile iOS"
	# 	elif "Windows" in device_string:
	# 		device_type = "Desktop Windows"
	# 	elif "Linux" in device_string and "Android" not in device_string:
	# 		device_type = "Desktop Linux"
	# 		# device_string_match.append({"Desktop Linux":fuzz.ratio(device_string,current_device_string)})
	# 		# device_string_match.append({"Unidentified":fuzz.ratio(device_string,current_device_string)})
	# 	device_string_match.append({"device_type":device_type,\
	# 			"match_percentage":device_match_percentage,\
	# 			"hash":device_hash})
	# 	redis_conn.hmset(client_id+":device_string_match",device_string_match)
	# if push_device_flag == 1:
	# 	acs_client_data.update_one({"hashed_card_number":client_hashed_card_number,
	# 					},{
	# 					'$push':{
	# 						'device_strings':current_device_string
	# 					}
	# 					})
	# if doc:
	# 	json_present = 1
	# if json_present == 0:
	# 	acs_client_data.insert_one({"hashed_card_number":client_hashed_card_number,
	# 						"device_strings":[cluster.return_device_id_string(jso)]
	# 					})
	
	
	return make_response(jsonify({"success":True,"message":"ok"}))

@app.route('/analysis_data',methods=['POST'])
def analysis_data():
	posted_json = request.get_json()
	client_id = posted_json.get("client_id")
	user = redis_conn.hgetall(client_id)
	client_hashed_card_number = redis_conn.get(client_id+":hashed_card_number")
	device_string_match = redis_conn.hgetall(client_id+":device_string_match")

	# device_string_match = [
 #    {
 #      "device_type": "Desktop Linux", 
 #      "hash": "4be26bfc1abb0a81d431b8edf2012f29c7e8d04726445f8d3b067716742834f95a387685644a39f915fe980f320c6b53eadd28e6f2b422257e49dfcc82ba1bc4", 
 #      "match_percentage": 62.6
 #    }, 
 #    {
 #      "device_type": "Desktop Linux", 
 #      "hash": "64f00f1d27942aed36480e9a43704fe25018d83eb0a8212190bcec4228368a8c861bc5df4d33100b2fd76bccff2968b721393d21b0662e5a2921c682c37a45a9", 
 #      "match_percentage": 100.0
 #    }
 #  ]
	return make_response(jsonify({"status":"ok","message":"success","device_string_match":device_string_match}))

# @app.route('/analysis_data',methods=['POST'])
# def analysis_data():
# 	posted_json = request.get_json()
# 	client_id = posted_json.get("client_id")
	
# 	jso = transaction_data.find_one({"client_id":client_id},
# 		sort=[( 'timestamp',DESCENDING )])
# 	user = acs_client_data.find_one({"client_id":client_id})
# 	current_device_string = cluster.return_device_id_string(jso)
# 	device_string_match = []
# 	push_device_flag = 1
# 	for device_string in user.get("device_strings",[]):
# 		userAgent = device_string.split("|")[19]
# 		device_match_percentage = cluster.return_fuzz_score_for_device(device_string,current_device_string)
# 		device_hash = hashlib.sha512(device_string).hexdigest()
# 		device_type = "Unidentified"
# 		if device_match_percentage >= 95:
# 			push_device_flag = 0
# 		# print userAgent
# 		if "Android" in device_string:
# 			device_type = "Mobile Android"
# 		elif "iPhone" in device_string:
# 			device_type = "Mobile iOS"
# 		elif "Windows" in device_string:
# 			device_type = "Desktop Windows"
# 		elif "Linux" in device_string and "Android" not in device_string:
# 			device_type = "Desktop Linux"
# 			# device_string_match.append({"Desktop Linux":fuzz.ratio(device_string,current_device_string)})
# 			# device_string_match.append({"Unidentified":fuzz.ratio(device_string,current_device_string)})
# 		device_string_match.append({"device_type":device_type,\
# 				"match_percentage":device_match_percentage,\
# 				"hash":device_hash})
# 	if push_device_flag == 1:
# 		acs_client_data.update_one({"client_id":client_id,
# 						},{
# 						'$push':{
# 							'device_strings':current_device_string
# 						}
# 						})
# 	return make_response(jsonify({"success":True,"message":"ok","device_string_match":device_string_match}))


@app.route("/give_json/<emp_id>",methods=["POST","GET"])
def give_json(emp_id):
	if request.method == "GET":
		response_json = []
		for p in login_data.find():
			del p["_id"]
			response_json.append(p)

		# for ele in os.walk("json_storage/"):
		# 	for filer in ele[2]:
		# 		if str(filer).split("|")[0] == emp_id:
		# 			response_json.append(json.loads(open("json_storage/"+filer,"r").read()))
		return make_response(jsonify(response_json))

def hashed_string(json_dict,hashed=0):
	hash_string = ""
	for key in json_dict.get("navigator",{}).keys():
		if key is not "keyArray" and key is not "mouseEvents":
			hash_string+=str(json_dict.get("navigator",{}).get(key,""))+"|"
	# print "hash_string",hash_string
	if hashed == 1:
		hash_string = hashlib.sha512(hash_string).hexdigest()
	return hash_string

@app.route("/give_excel/<emp_id>",methods=["GET"])
@app.route("/give_excel",methods=["GET"])
def give_excel(emp_id=""):
	if request.method == "GET":
		response_json = []
		records = login_data.find({"emp_id":emp_id})
		for record in records:
			response_json.append(record)
		# for ele in os.walk("json_storage/"):
		# 	for filer in ele[2]:
		# 		if emp_id == "":
		# 			response_json.append(json.loads(open("json_storage/"+filer,"r").read()))
		# for ele in os.walk("json_storage/"):
		# 	for filer in ele[2]:
		# 		if emp_id !="" and str(filer).split("|")[0] == emp_id:
		# 			response_json.append(json.loads(open("json_storage/"+filer,"r").read()))
		
		book = open_workbook('signature_template.xlsx')
		wb = copy(book)
		sheet = wb.get_sheet(0)
		next_row_count = 0
		for json_dict in response_json:
			sheet.write(next_row_count+1,0,json_dict.get('email',""))
			sheet.write(next_row_count+1,1,json_dict.get('emp_id',""))
			sheet.write(next_row_count+1,2,json_dict.get('name',""))
			for key_count,key_stroke in enumerate(json_dict.get("keyArray",[])):
				sheet.write(key_count+next_row_count+1,3,key_stroke.get('id',""))
				sheet.write(key_count+next_row_count+1,4,key_stroke.get('jumpTicks',""))
				sheet.write(key_count+next_row_count+1,5,key_stroke.get('keyCode',""))
				sheet.write(key_count+next_row_count+1,6,key_stroke.get('keyUpTicks',""))
			for mouse_count,mouse_entry in enumerate(json_dict.get("mouseEvents",[])):
				sheet.write(mouse_count+next_row_count+1,7,mouse_entry.get('x',""))
				sheet.write(mouse_count+next_row_count+1,8,mouse_entry.get('y',""))
			sheet.write(next_row_count+1,9,json_dict.get("navigator",{}).get('appCodeName',""))
			sheet.write(next_row_count+1,10,json_dict.get("navigator",{}).get('appName',""))
			sheet.write(next_row_count+1,11,json_dict.get("navigator",{}).get('appVersion',""))
			sheet.write(next_row_count+1,12,json_dict.get("navigator",{}).get('cookieEnabled',""))
			sheet.write(next_row_count+1,13,json_dict.get("navigator",{}).get('height',""))
			sheet.write(next_row_count+1,14,json_dict.get("navigator",{}).get('width',""))
			sheet.write(next_row_count+1,15,json_dict.get("navigator",{}).get('javaEnabled',""))
			for mime_count,mimetype in enumerate(json_dict.get("navigator",{}).get("mimetypes",[])):
				sheet.write(mime_count+next_row_count+1,16,mimetype)
			for plugin_count,plugin in enumerate(json_dict.get("navigator",{}).get("plugins",[])):
				sheet.write(plugin_count+next_row_count+1,19,plugin)
			sheet.write(next_row_count+1,17,json_dict.get("navigator",{}).get('onLine',""))
			sheet.write(next_row_count+1,18,json_dict.get("navigator",{}).get('platform',""))
			sheet.write(next_row_count+1,20,json_dict.get("navigator",{}).get('product',""))
			sheet.write(next_row_count+1,21,json_dict.get("navigator",{}).get('timezone',""))
			sheet.write(next_row_count+1,22,json_dict.get("navigator",{}).get('userAgent',""))
			sheet.write(next_row_count+1,23,json_dict.get("navigator",{}).get('vendor',""))
			sheet.write(next_row_count+1,24,str(json_dict.get("navigator",{}).get('localStorage',"")))
			sheet.write(next_row_count+1,25,hashlib.sha512(json_dict.get("navigator",{}).get('canvas',"")).hexdigest())
			if "Mobile" in json_dict.get("navigator",{}).get('userAgent',""):
				sheet.write(next_row_count+1,26,"Mobile")
			else:
				sheet.write(next_row_count+1,26,"Desktop")
			sheet.write(next_row_count+1,27,str(json_dict.get("navigator",{}).get('colorDepth',"")))
			sheet.write(next_row_count+1,28,str(json_dict.get("navigator",{}).get('language',"")))
			sheet.write(next_row_count+1,29,str(json_dict.get("navigator",{}).get('doNotTrack',"")))
			sheet.write(next_row_count+1,30,str(json_dict.get("navigator",{}).get('productSub',"")))
			sheet.write(next_row_count+1,31,str(json_dict.get("navigator",{}).get('maxTouchPoints',"")))
			sheet.write(next_row_count+1,32,str(json_dict.get("navigator",{}).get('connection_downlink',"")))
			sheet.write(next_row_count+1,33,str(json_dict.get("navigator",{}).get('connection_effectiveType',"")))
			sheet.write(next_row_count+1,34,str(json_dict.get("navigator",{}).get('connection_rtt',"")))
			sheet.write(next_row_count+1,35,str(json_dict.get("navigator",{}).get('webGLVendor',"")))
			sheet.write(next_row_count+1,36,str(json_dict.get("navigator",{}).get('webGLRenderer',"")))
			for font_count,font in enumerate(json_dict.get("navigator",{}).get("fonts",[])):
				sheet.write(plugin_count+next_row_count+1,19,font)
			hash_string = ""
			print json_dict.get("navigator",{}).keys()
			hash_string = hashed_string(json_dict,hashed=1)
			sheet.write(next_row_count+1,37,hash_string)
			next_row_count += max(len(json_dict.get("keyArray",[])),len(json_dict.get("mouseEvents",[])),len(json_dict.get("navigator",{}).get("mimetypes",[])),len(json_dict.get("navigator",{}).get("plugins",[])),len(json_dict.get("navigator",{}).get("fonts",[])))+1

		if emp_id == "":
			emp_id = "all"
		filename = "excel_files/{}-{}.xlsx".format(emp_id,str(int(time.time()))[:10])
		wb.save(filename)
		xls = open(filename, 'r').read()
		return Response(xls, mimetype="application/vnd.ms-excel"\
			, headers={"Content-disposition":"attachment; filename={}".format(filename)})

def keyboard_analyze(keyboard_feature,key_array):
	mean_arr = []
	if keyboard_feature == "mean_dwell_time":
		for sample in key_array:
			sum_value = 0
			count = 0
			for key_dict in sample:
				sum_value += key_dict.get("keyUpTicks",0)
				count+=1
			mean_arr = numpy.append(mean_arr,float(sum_value/float(count)))
	if keyboard_feature == "mean_flight_time":
		for sample in key_array:
			sum_value = 0
			count = 0
			for index,key_dict in enumerate(sample):
				if index>0:
					sum_value += key_dict.get("jumpTicks",0)
					count+=1
			mean_arr = numpy.append(mean_arr,float(sum_value/float(count)))
	if keyboard_feature == "mean_trigraph_time":
		for sample in key_array:
			sum_value = 0
			count = 0
			for index in range(len(sample)-2):
				sum_value += float(sample[index].get("keyUpTicks",0))+float(sample[index+1].get("jumpTicks",0))+float(sample[index+1].get("keyUpTicks",0))+float(sample[index+2].get("jumpTicks",0))+float(sample[index+2].get("keyUpTicks",0))
				count+=1
			mean_arr = numpy.append(mean_arr,float(sum_value/float(count)))
	if keyboard_feature == "mean_typing_speed":
		for sample in key_array:
			sum_value = 0
			count = 0
			for index,element in enumerate(sample):
				if index>1:
					sum_value += element.get("jumpTicks",0)
				else:
					sum_value += element.get("jumpTicks",0)
					sum_value += element.get("keyUpTicks",0)
				count+=1
			mean_arr = numpy.append(mean_arr,float(sum_value/float(count)))
			# for index in range(len(sample)-2):
			# 	sum_value += float(sample[index].get("keyUpTicks",0))+float(sample[index+1].get("jumpTicks",0))+float(sample[index+1].get("keyUpTicks",0))+float(sample[index+2].get("jumpTicks",0))+float(sample[index+2].get("keyUpTicks",0))
			# 	count+=1
			# mean_arr = numpy.append(mean_arr,float(sum_value/float(count)))
	return mean_arr

def octant_by_degree(angle):
	quadrant = 0
	if angle < 0:
		angle = 360.0+angle
	for count,degree in enumerate(range(0,360,45)):
		if angle >= degree and angle < degree+45:
			quadrant = count
			break
	return quadrant

def replace_zero_with_approximation(value):
	if value == 0:
		return 0.00000001
	else:
		return value

def mouse_analyze(mouse_feature,mouse_events,octant=1):
	feature_arr = []
	if mouse_feature == "mouse_action_per_direction":
		# print "mouse_events",mouse_events
		for sample in mouse_events:
			octant_arr = [0,0,0,0,0,0,0,0]
			for index in range(len(sample)-1):
				# print "index",index
				octant_arr[octant_by_degree(math.degrees(math.atan(float(float(sample[index+1].get("y"))-float(sample[index].get("y")))/replace_zero_with_approximation(float(float(sample[index+1].get("x"))-float(sample[index].get("x")))))))]+=1
			# print "feature_arr",feature_arr,"octant",octant_arr
			feature_arr = numpy.append(feature_arr,float(octant_arr[octant])/float(sum(octant_arr))*100)
		return feature_arr
	if mouse_feature == "mouse_distance_per_direction":
		for sample in mouse_events:
			octant_arr = [0,0,0,0,0,0,0,0]
			for index in range(len(sample)-1):
				octant_arr[octant_by_degree(math.degrees(math.atan(float(float(sample[index+1].get("y"))-float(sample[index].get("y")))/replace_zero_with_approximation(float(float(sample[index+1].get("x"))-float(sample[index].get("x")))))))]+=((float(sample[index+1].get("y"))-float(sample[index].get("y")))**2+(float(sample[index+1].get("x"))-float(sample[index].get("x")))**2)**0.5
			feature_arr = numpy.append(feature_arr,float(octant_arr[octant])/float(sum(octant_arr))*100)
		return feature_arr
	if mouse_feature == "mouse_time_per_direction":
		for sample in mouse_events:
			octant_arr = [0,0,0,0,0,0,0,0]
			for index in range(len(sample)-1):
				octant_arr[octant_by_degree(math.degrees(math.atan(float(float(sample[index+1].get("y"))-float(sample[index].get("y")))/replace_zero_with_approximation(float(float(sample[index+1].get("x"))-float(sample[index].get("x")))))))]+=float(sample[index+1].get("timestamp"))-float(sample[index].get("timestamp"))
			feature_arr = numpy.append(feature_arr,float(octant_arr[octant])/float(sum(octant_arr))*100)
		return feature_arr
	if mouse_feature == "mouse_average_distance_per_direction":
		for sample in mouse_events:
			octant_arr = [0,0,0,0,0,0,0,0]
			for index in range(len(sample)-1):
				octant_arr[octant_by_degree(math.degrees(math.atan(float(float(sample[index+1].get("y"))-float(sample[index].get("y")))/replace_zero_with_approximation(float(float(sample[index+1].get("x"))-float(sample[index].get("x")))))))]+=((float(sample[index+1].get("y"))-float(sample[index].get("y")))**2+(float(sample[index+1].get("x"))-float(sample[index].get("x")))**2)**0.5
			feature_arr = numpy.append(feature_arr,float(octant_arr[octant])/8.0)
		return feature_arr
	if mouse_feature == "mouse_average_speed_per_direction":
		for sample in mouse_events:
			octant_arr = [0,0,0,0,0,0,0,0]
			for index in range(len(sample)-1):
				octant_arr[octant_by_degree(math.degrees(math.atan(float(float(sample[index+1].get("y"))-float(sample[index].get("y")))/replace_zero_with_approximation(float(float(sample[index+1].get("x"))-float(sample[index].get("x")))))))]+=((float(sample[index+1].get("y"))-float(sample[index].get("y")))**2+(float(sample[index+1].get("x"))-float(sample[index].get("x")))**2)**0.5/(float(sample[index+1].get("timestamp"))-float(sample[index].get("timestamp")))
			feature_arr = numpy.append(feature_arr,float(octant_arr[octant])/8.0)
		return feature_arr
	if mouse_feature == "mouse_average_velocity_x_per_direction":
		for sample in mouse_events:
			octant_arr = [0,0,0,0,0,0,0,0]
			for index in range(len(sample)-1):
				octant_arr[octant_by_degree(math.degrees(math.atan(float(float(sample[index+1].get("y"))-float(sample[index].get("y")))/replace_zero_with_approximation(float(float(sample[index+1].get("x"))-float(sample[index].get("x")))))))]+=(float(sample[index+1].get("x"))-float(sample[index].get("x")))/(float(sample[index+1].get("timestamp"))-float(sample[index].get("timestamp")))
			feature_arr = numpy.append(feature_arr,float(octant_arr[octant])/8.0)
		return feature_arr
	if mouse_feature == "mouse_average_velocity_y_per_direction":
		for sample in mouse_events:
			octant_arr = [0,0,0,0,0,0,0,0]
			for index in range(len(sample)-1):
				octant_arr[octant_by_degree(math.degrees(math.atan(float(float(sample[index+1].get("y"))-float(sample[index].get("y")))/replace_zero_with_approximation(float(float(sample[index+1].get("x"))-float(sample[index].get("x")))))))]+=(float(sample[index+1].get("y"))-float(sample[index].get("y")))/(float(sample[index+1].get("timestamp"))-float(sample[index].get("timestamp")))
			feature_arr = numpy.append(feature_arr,float(octant_arr[octant])/8.0)
		return feature_arr


def cross_analyze(mouse_events,key_array,mouse_feature,keyboard_feature,octant):
	keyboard_analytics = keyboard_analyze(keyboard_feature,key_array)
	mouse_analytics = mouse_analyze(mouse_feature,mouse_events,octant)
	g = lambda x,y : {'x':x,'y':y}
	cross_analyze_list = []
	for data in zip(mouse_analytics, keyboard_analytics):
		cross_analyze_list.append(g(data[0],data[1]))

	return cross_analyze_list


@app.route("/analysis",methods=["GET","POST"])
def analysis():
	if request.method == "GET":
		return make_response(render_template("chart.html"))
	if request.method == "POST":
		user1_id = request.form.get("user1_id")
		mouse_feature = request.form.get("mouse_feature")
		keyboard_feature = request.form.get("keyboard_feature")
		octant = request.form.get("octant",1)
		# print "octants",octant_by_degree(10),octant_by_degree(55),octant_by_degree(100),octant_by_degree(145),octant_by_degree(190)
		response_json = []
		for ele in os.walk("json_storage/"):
			for filer in ele[2]:
				if user1_id == "":
					response_json.append(json.loads(open("json_storage/"+filer,"r").read()))
		for ele in os.walk("json_storage/"):
			for filer in ele[2]:
				if user1_id !="" and str(filer).split("|")[0] == user1_id:
					response_json.append(json.loads(open("json_storage/"+filer,"r").read()))
		mouse_events = []
		key_array = []
		for json_dict in response_json:
			mouse_events.append(json_dict.get("mouseEvents"))
			key_array.append(json_dict.get("keyArray"))
		response = cross_analyze(mouse_events,key_array,mouse_feature,keyboard_feature,int(octant)-1)
		return jsonify({"response":response,"labels":[mouse_feature,keyboard_feature]})

def gaussian_analyze(response_json,emp_id):
	print "hello gaussian analysis"
	print "len response_json",len(response_json)
	users = []
	data = []
	check = "0"
	mouse_cluster_data = [0,0,0,0,0,0,0]
	keyboard_cluster_data = [0,0,0,0]
	case_identifier = ""
	mouse_analysis_data = []
	keyboard_analysis_data = []
	fraud_included_status_data = []
	fraud_included_mouse_analysis_data = []
	fraud_included_keyboard_analysis_data = []
	test_data_arr = []
	test_user_data = []
	keyboard_cluster_points = []
	mouse_cluster_points = []
	fraud_check = lambda x:1 if x=="FRAUD" else 2
	for response in response_json:
		fraud_included_status_data.append(fraud_check(response.get("status")))
		fraud_included_keyboard_analysis_data.append(response.get("keyArray",[]))
		fraud_included_mouse_analysis_data.append(response.get("mouseEvents",[]))
		# if response.get("status","") == "VERIFIED":
		data.append(response)
		# mouse_analysis_data.append(response.get("mouseEvents",[]))
		# keyboard_analysis_data.append(response.get("keyArray",[]))
		flag = 0
		for user in users:
			if user.get('emp_id') == response.get("emp_id"):
				flag = 1
		if flag == 0:
			users.append({"emp_id":response_json[0].get("emp_id"),"name":response_json[0].get("name")})
	# print "data_0",data[0].get("emp_id","")
	m_a_p_d = mouse_analyze("mouse_action_per_direction",fraud_included_mouse_analysis_data,1)
	m_t_p_d = mouse_analyze("mouse_time_per_direction",fraud_included_mouse_analysis_data,1)
	m_d_p_d = mouse_analyze("mouse_distance_per_direction",fraud_included_mouse_analysis_data,1)
	m_a_d_p_d = mouse_analyze("mouse_average_distance_per_direction",fraud_included_mouse_analysis_data,1)
	m_a_s_p_d = mouse_analyze("mouse_average_speed_per_direction",fraud_included_mouse_analysis_data,1)
	m_a_v_x_p_d = mouse_analyze("mouse_average_velocity_x_per_direction",fraud_included_mouse_analysis_data,1)
	m_a_v_y_p_d = mouse_analyze("mouse_average_velocity_y_per_direction",fraud_included_mouse_analysis_data,1)
	m_d_t = keyboard_analyze("mean_dwell_time",fraud_included_keyboard_analysis_data)
	m_f_t = keyboard_analyze("mean_flight_time",fraud_included_keyboard_analysis_data)
	m_t_t = keyboard_analyze("mean_trigraph_time",fraud_included_keyboard_analysis_data)
	m_t_s = keyboard_analyze("mean_typing_speed",fraud_included_keyboard_analysis_data)
	for count in range(len(fraud_included_mouse_analysis_data)):
		# feature_list = [m_a_p_d[count],m_t_p_d[count],m_d_p_d[count]]
		# feature_list = [m_d_t[count],m_f_t[count],m_t_t[count]]
		feature_list = [m_a_p_d[count],m_t_p_d[count],m_d_p_d[count],m_a_d_p_d[count],m_a_s_p_d[count],m_a_v_x_p_d[count],m_a_v_y_p_d[count]]
		mouse_cluster_points.append(feature_list)
	for count in range(len(fraud_included_keyboard_analysis_data)):
		# feature_list = [m_a_p_d[count],m_t_p_d[count],m_d_p_d[count]]
		# feature_list = [m_d_t[count],m_f_t[count],m_t_t[count]]
		feature_list = [m_d_t[count],m_f_t[count],m_t_t[count],m_t_s[count]]
		keyboard_cluster_points.append(feature_list)

	for count,response in enumerate(response_json):
		print "count is",count
		device_string_match = []
		print "response status",response.get("status","")
		if response.get("emp_id") == emp_id and response.get("status","") == "PENDING":
			# print response.get("emp_id")+"|"+response.get("timestamp")
			# print response.get("mouseEvents",[])
			# print "mouse_arr",response.get("mouseEvents",[])
			# print "mouse_arr",mouse_analyze("mouse_action_per_direction",,1)[0]
			channel = response.get("channel","WEB")
			current_device_string = cluster.return_device_id_string(response,channel)
			user = user_data.find_one({"emp_id":emp_id})

			print len(user.get("device_strings",[]))
			for device_string in user.get("device_strings",[]):
				userAgent = device_string.split("|")[19]
				# print userAgent
				print userAgent
				# if "Android" in device_string:
				# 	device_string_match.append({"Mobile Android":fuzz.ratio(device_string,current_device_string)})
				# elif "iPhone" in device_string:
				# 	device_string_match.append({"Mobile iOS":fuzz.ratio(device_string,current_device_string)})
				# elif "Windows" in device_string:
				# 	device_string_match.append({"Desktop Windows":fuzz.ratio(device_string,current_device_string)})
				# elif "Linux" in device_string and "Android" not in device_string:
				# 	device_string_match.append({"Desktop Linux":fuzz.ratio(device_string,current_device_string)})
				# else:
				# 	device_string_match.append({"Unidentified":fuzz.ratio(device_string,current_device_string)})
			
				if "Android" in device_string:
					device_string_match.append({"Mobile Android":cluster.return_fuzz_score_for_device(device_string,
						current_device_string,channel)})
				elif "iPhone" in device_string:
					device_string_match.append({"Mobile iOS":cluster.return_fuzz_score_for_device(device_string,
						current_device_string,channel)})
				elif "Windows" in device_string:
					device_string_match.append({"Desktop Windows":cluster.return_fuzz_score_for_device(device_string,
						current_device_string,channel)})
				elif "Linux" in device_string and "Android" not in device_string:
					device_string_match.append({"Desktop Linux":cluster.return_fuzz_score_for_device(device_string,
						current_device_string,channel)})
				else:
					device_string_match.append({"Unidentified":cluster.return_fuzz_score_for_device(device_string,
						current_device_string,channel)})
			
			hash_string = ""
			for key in response.get("navigator",{}).keys():
				if key is not "keyArray" and key is not "mouseEvents":
					hash_string+=str(response.get("navigator",{}).get(key,""))+"|"
			hash_string = hashlib.sha512(hash_string).hexdigest()
			test_user_data = [response.get("name"),response.get("emp_id"),response.get("email"),hash_string]
			# test_data_arr = [keyboard_analyze("mean_dwell_time",[response.get("keyArray",[])])[0],
			# 				keyboard_analyze("mean_flight_time",[response.get("keyArray",[])])[0],
			# 				keyboard_analyze("mean_trigraph_time",[response.get("keyArray",[])])[0]]
			mouse_test_data_arr = [mouse_analyze("mouse_action_per_direction",[response.get("mouseEvents",[])],1)[0],
							mouse_analyze("mouse_time_per_direction",[response.get("mouseEvents",[])],1)[0],
							mouse_analyze("mouse_distance_per_direction",[response.get("mouseEvents",[])],1)[0],
							mouse_analyze("mouse_average_distance_per_direction",[response.get("mouseEvents",[])],1)[0],
							mouse_analyze("mouse_average_speed_per_direction",[response.get("mouseEvents",[])],1)[0],
							mouse_analyze("mouse_average_velocity_x_per_direction",[response.get("mouseEvents",[])],1)[0],
							mouse_analyze("mouse_average_velocity_y_per_direction",[response.get("mouseEvents",[])],1)[0]]
			keyboard_test_data_arr = [keyboard_analyze("mean_dwell_time",[response.get("keyArray",[])])[0],
							keyboard_analyze("mean_flight_time",[response.get("keyArray",[])])[0],
							keyboard_analyze("mean_trigraph_time",[response.get("keyArray",[])])[0],
							keyboard_analyze("mean_typing_speed",[response.get("keyArray",[])])[0]]
			check = 1
			case_identifier = response['emp_id']+"|"+response['timestamp']
			# print "mouse test cluster data",mouse_cluster_points,mouse_test_data_arr
			print "generating_confidence_gaussian"
			mouse_cluster_data = cluster.generate_confidence_gaussian(mouse_cluster_points,fraud_included_status_data,mouse_test_data_arr)
			keyboard_cluster_data = cluster.generate_confidence_gaussian(keyboard_cluster_points,fraud_included_status_data,keyboard_test_data_arr)
			
			break

	return mouse_cluster_data,keyboard_cluster_data

@app.route('/case_manager/<emp_id>',methods=["GET"])
@app.route('/mark_verified/<emp_id>',methods=["POST"])
@app.route('/mark_fraud/<emp_id>',methods=["POST"])
def case_manager(emp_id):
	if request.method == "GET":

		response_json = []
		for jso in login_data.find({"emp_id":emp_id}):
			print jso.get("status")
			response_json.append(jso)
		gaussian_kb,gaussian_mouse = gaussian_analyze(response_json,emp_id)
		print "gaussian_kb",gaussian_kb
		print "gaussian_mouse",gaussian_mouse
		# print "resp_json_count",response_json
		# for ele in os.walk("json_storage/"):
		# 	for filer in ele[2]:
		# 		if emp_id !="" and str(filer).split("|")[0] == emp_id:
		# 			jso = json.loads(open("json_storage/"+filer,"r").read())
		# 			jso['timestamp'] = str(str(filer).split("|")[1]).split(".")[0]
		# 			jso["datetime"] =  datetime.datetime.strftime(datetime.datetime.fromtimestamp(int(jso['timestamp'])),"%Y-%m-%d %H:%M:%S")
		# 			response_json.append(jso)
		
		users = []
		data = []
		check = "0"
		mouse_cluster_data = [0,0,0,0,0,0,0]
		keyboard_cluster_data = [0,0,0,0]
		case_identifier = ""
		mouse_analysis_data = []
		keyboard_analysis_data = []
		fraud_included_status_data = []
		fraud_included_mouse_analysis_data = []
		fraud_included_keyboard_analysis_data = []
		test_data_arr = []
		test_user_data = []
		keyboard_cluster_points = []
		mouse_cluster_points = []
		for response in response_json:
			fraud_included_status_data.append(response.get("status"))
			fraud_included_keyboard_analysis_data.append(response.get("keyArray",[]))
			fraud_included_mouse_analysis_data.append(response.get("mouseEvents",[]))
			if response.get("status","") == "VERIFIED":
				data.append(response)
				mouse_analysis_data.append(response.get("mouseEvents",[]))
				keyboard_analysis_data.append(response.get("keyArray",[]))
			flag = 0
			for user in users:
				if user.get('emp_id') == response.get("emp_id"):
					flag = 1
			if flag == 0:
				users.append({"emp_id":response_json[0].get("emp_id"),"name":response_json[0].get("name")})
		# print "data_0",data[0].get("emp_id","")
		m_a_p_d = mouse_analyze("mouse_action_per_direction",mouse_analysis_data,1)
		m_t_p_d = mouse_analyze("mouse_time_per_direction",mouse_analysis_data,1)
		m_d_p_d = mouse_analyze("mouse_distance_per_direction",mouse_analysis_data,1)
		m_a_d_p_d = mouse_analyze("mouse_average_distance_per_direction",mouse_analysis_data,1)
		m_a_s_p_d = mouse_analyze("mouse_average_speed_per_direction",mouse_analysis_data,1)
		m_a_v_x_p_d = mouse_analyze("mouse_average_velocity_x_per_direction",mouse_analysis_data,1)
		m_a_v_y_p_d = mouse_analyze("mouse_average_velocity_y_per_direction",mouse_analysis_data,1)
		m_d_t = keyboard_analyze("mean_dwell_time",keyboard_analysis_data)
		m_f_t = keyboard_analyze("mean_flight_time",keyboard_analysis_data)
		m_t_t = keyboard_analyze("mean_trigraph_time",keyboard_analysis_data)
		m_t_s = keyboard_analyze("mean_typing_speed",keyboard_analysis_data)
		for count in range(len(keyboard_analysis_data)):
			# feature_list = [m_a_p_d[count],m_t_p_d[count],m_d_p_d[count]]
			# feature_list = [m_d_t[count],m_f_t[count],m_t_t[count]]
			feature_list = [m_a_p_d[count],m_t_p_d[count],m_d_p_d[count],m_a_d_p_d[count],m_a_s_p_d[count],m_a_v_x_p_d[count],m_a_v_y_p_d[count]]
			mouse_cluster_points.append(feature_list)
		for count in range(len(mouse_analysis_data)):
			# feature_list = [m_a_p_d[count],m_t_p_d[count],m_d_p_d[count]]
			# feature_list = [m_d_t[count],m_f_t[count],m_t_t[count]]
			feature_list = [m_d_t[count],m_f_t[count],m_t_t[count],m_t_s[count]]
			keyboard_cluster_points.append(feature_list)

		for response in response_json:
			device_string_match = []
			if response.get("emp_id") == emp_id and response.get("status","") == "PENDING":
				channel = response.get("channel","WEB")
				# print response.get("emp_id")+"|"+response.get("timestamp")
				# print response.get("mouseEvents",[])
				# print "mouse_arr",response.get("mouseEvents",[])
				# print "mouse_arr",mouse_analyze("mouse_action_per_direction",,1)[0]
				current_device_string = cluster.return_device_id_string(response,channel)
				user = user_data.find_one({"emp_id":emp_id})

				print len(user.get("device_strings",[]))
				for device_string in user.get("device_strings",[]):
					userAgent = device_string.split("|")[19]
					# print userAgent
					print userAgent
					if "Android" in device_string:
						fuzz_score_response = cluster.return_fuzz_score_for_device(device_string,
							current_device_string,channel)
						match_score = fuzz_score_response[0]
						user_agent_response = fuzz_score_response[2]
						device_string_match.append({"Mobile Android":[match_score,user_agent_response]})
					elif "iPhone" in device_string:
						fuzz_score_response = cluster.return_fuzz_score_for_device(device_string,
							current_device_string,channel)
						match_score = fuzz_score_response[0]
						user_agent_response = fuzz_score_response[2]
						device_string_match.append({"Mobile iOS":[match_score,user_agent_response]})
					elif "Windows" in device_string:
						fuzz_score_response = cluster.return_fuzz_score_for_device(device_string,
							current_device_string,channel)
						match_score = fuzz_score_response[0]
						user_agent_response = fuzz_score_response[2]
						device_string_match.append({"Desktop Windows":[match_score,user_agent_response]})
					elif "Linux" in device_string and "Android" not in device_string:
						fuzz_score_response = cluster.return_fuzz_score_for_device(device_string,
							current_device_string,channel)
						match_score = fuzz_score_response[0]
						user_agent_response = fuzz_score_response[2]
						device_string_match.append({"Desktop Linux":[match_score,user_agent_response]})
					else:
						fuzz_score_response = cluster.return_fuzz_score_for_device(device_string,
							current_device_string,channel)
						match_score = fuzz_score_response[0]
						user_agent_response = fuzz_score_response[2]
						device_string_match.append({"Unidentified":[match_score,user_agent_response]})
				
				hash_string = ""
				for key in response.get("navigator",{}).keys():
					if key is not "keyArray" and key is not "mouseEvents":
						hash_string+=str(response.get("navigator",{}).get(key,""))+"|"
				hash_string = hashlib.sha512(hash_string).hexdigest()
				test_user_data = [response.get("name"),response.get("emp_id"),response.get("email"),hash_string]
				# test_data_arr = [keyboard_analyze("mean_dwell_time",[response.get("keyArray",[])])[0],
				# 				keyboard_analyze("mean_flight_time",[response.get("keyArray",[])])[0],
				# 				keyboard_analyze("mean_trigraph_time",[response.get("keyArray",[])])[0]]
				mouse_test_data_arr = [mouse_analyze("mouse_action_per_direction",[response.get("mouseEvents",[])],1)[0],
								mouse_analyze("mouse_time_per_direction",[response.get("mouseEvents",[])],1)[0],
								mouse_analyze("mouse_distance_per_direction",[response.get("mouseEvents",[])],1)[0],
								mouse_analyze("mouse_average_distance_per_direction",[response.get("mouseEvents",[])],1)[0],
								mouse_analyze("mouse_average_speed_per_direction",[response.get("mouseEvents",[])],1)[0],
								mouse_analyze("mouse_average_velocity_x_per_direction",[response.get("mouseEvents",[])],1)[0],
								mouse_analyze("mouse_average_velocity_y_per_direction",[response.get("mouseEvents",[])],1)[0]]
				keyboard_test_data_arr = [keyboard_analyze("mean_dwell_time",[response.get("keyArray",[])])[0],
								keyboard_analyze("mean_flight_time",[response.get("keyArray",[])])[0],
								keyboard_analyze("mean_trigraph_time",[response.get("keyArray",[])])[0],
								keyboard_analyze("mean_typing_speed",[response.get("keyArray",[])])[0]]
				check = 1
				case_identifier = response['emp_id']+"|"+response['timestamp']
				# print "mouse test cluster data",mouse_cluster_points,mouse_test_data_arr
				mouse_cluster_data = cluster.generate_confidence(mouse_cluster_points,mouse_test_data_arr)
				keyboard_cluster_data = cluster.generate_confidence(keyboard_cluster_points,keyboard_test_data_arr)
				
				break



		# print "mouse_action_per_direction",
		# print "mouse_time_per_direction",
		# print "mouse_distance_per_direction",
		# print "mean_dwell_time",
		# print "mean_flight_time",keyboard_analyze("mean_flight_time",keyboard_analysis_data)
		# print "mean_trigraph_time",keyboard_analyze("mean_trigraph_time",keyboard_analysis_data)
		print "gaussian_kb",gaussian_kb
		print "gaussian_mouse",gaussian_mouse
		print "device_string_match",device_string_match
		return make_response(render_template("case_manager.html",users=users,
								data=data,
								check=check,
								mouse_cluster_data=mouse_cluster_data,
								keyboard_cluster_data=keyboard_cluster_data,
								gaussian_kb=gaussian_kb,
								gaussian_mouse=gaussian_mouse,
								case_identifier=case_identifier,
								test_user_data=test_user_data,
								device_string_match=device_string_match))
	if request.method == "POST":
		case_identifier = request.form.get("case_identifier")
		
		emp_id = str(case_identifier).split("|")[0]
		timestamp = str(case_identifier).split("|")[1]

		# print "case_identifier",case_identifier
		# file_r = open("json_storage/"+case_identifier+".json","r")
		if request.path == "/mark_verified/"+str(emp_id):
			jso = login_data.find_one({"emp_id":emp_id,"timestamp":timestamp})
			login_data.update_one({"emp_id":emp_id,"timestamp":timestamp},{
			'$set': {
			'status': "VERIFIED"
			}
			}, upsert=False)
			user = user_data.find_one({"emp_id":emp_id})
			device_strings = user.get("device_string",[])
			current_device_string = cluster.return_device_id_string(jso)
			max_match = 0
			for device_string in user.get("device_strings",[]):
				if fuzz.ratio(device_string,current_device_string) >= max_match:
					max_match = fuzz.ratio(device_string,current_device_string)
			if max_match < 90:
				user_data.update_one({"emp_id":emp_id,
							},{
							'$push':{
								'device_strings':current_device_string
							}
							})

			# data = file_r.read()
			# jso = json.loads(data)
			# jso['status'] = "VERIFIED"
			# file_w = open("json_storage/"+case_identifier+".json","w")
			# file_w.write(json.dumps(jso))
		if request.path == "/mark_fraud/"+str(emp_id):
			jso = login_data.find_one({"emp_id":emp_id,"timestamp":timestamp})
			login_data.update_one({"emp_id":emp_id,"timestamp":timestamp},{
			'$set': {
			'status': "FRAUD"
			}
			}, upsert=False)
			# data = file_r.read()
			# jso = json.loads(data)
			# jso['status'] = "FRAUD"
			# file_w = open("json_storage/"+case_identifier+".json","w")
			# file_w.write(json.dumps(jso))
		return redirect("/case_manager/"+emp_id)

@app.route('/fuzzy_email',methods=["GET","POST"])
def fuzzy_email():
	if request.method == "GET":
		return render_template("email_fuzzy.html",show_analysis=False)
	if request.method == "POST":
		test_email = request.form.get("test_email","")
		f = open("fuzzy_match/fuzz.json","r")
		email_bank = json.loads(f.read())
		email_list = email_bank["email_list"]
		matches = []
		new_email_list = []
		for email in email_list:
			if fuzz.ratio(test_email,email) > 30 and test_email != email:
				matches.append({"test_string":test_email,"matched_string":email,"percent":fuzz.ratio(test_email,email)})
		email_list.append(test_email)
		w = open("fuzzy_match/fuzz.json","w")
		w.write(json.dumps({"email_list":email_list}))
		return render_template("email_fuzzy.html",show_analysis=True,matches=matches)



if __name__ == '__main__':
	app.run("0.0.0.0",port=3131,debug=True,threaded=True)
