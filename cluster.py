from sklearn.cluster import KMeans
from sklearn.naive_bayes import GaussianNB
from manifest import NAVIGATOR_KEY_LIST,\
NAVIGATOR_KEY_SCORE_MAP,MOBILE_WEB_NAVIGATOR_KEY_LIST,MOBILE_WEB_NAVIGATOR_KEY_SCORE_MAP
import numpy
import math
from fuzzywuzzy import fuzz
# from mpl_toolkits.mplot3d import Axes3D
# import matplotlib.pyplot as plt
import numpy as np
import httpagentparser
import json

def replace_zero_with_approximation(value):
	if value == 0:
		return 0.00000001
	else:
		return value

def distance_from_center(cluster_centers,point):
	sum = 0
	print "<<< err point >>>",point
	for count,dim in enumerate(point):
		val = (cluster_centers[count]-dim)**2
		sum+=val
	return sum**0.5

# train = numpy.array([[1,2,3],[1.5,2.5,3.5],[1,3,5],[1,3,6]])
# 
# [[1,2],[1.5,2.5],[1,6],[1,3],[1.125,2.2],[1.125,3.14]]
def generate_confidence(train_data,login_data):
	train = numpy.array(train_data)
	# fig = plt.figure()
	# ax = fig.add_subplot(111, projection='3d')
	kmeans = KMeans(n_clusters=1,max_iter=100).fit(train)
	dist_arr = numpy.array([])
	for point in train:
		# ax.scatter(point[0], point[1], point[2], c='b', marker='o')
		dist_arr = numpy.append(dist_arr,distance_from_center(kmeans.cluster_centers_[0],point))
	
	# ax.scatter(kmeans.cluster_centers_[0][0], kmeans.cluster_centers_[0][1], kmeans.cluster_centers_[0][2], c='r', marker='^')

	arr = login_data
	# ax.scatter(login_data[0], login_data[1], login_data[2], c='g', marker='*')
	zero_or_up = lambda x:0 if x < 0 else x
	max_dist = numpy.max(dist_arr)
	dist_from_center = distance_from_center(kmeans.cluster_centers_[0],arr)
	confidence = zero_or_up(1-(distance_from_center(kmeans.cluster_centers_[0],arr)/replace_zero_with_approximation(float(numpy.max(dist_arr)))))*100

	# print "cluster_center",kmeans.cluster_centers_[0]
	# print "prediction",kmeans.predict([arr])
	# print "dist",distance_from_center(kmeans.cluster_centers_[0],arr),numpy.mean(dist_arr)
	# print "confidence",confidence,"%"
	
	

	# ax.set_xlabel('Mean Dwell Time')
	# ax.set_ylabel('Mean Flight Time')
	# ax.set_zlabel('Mean Trigraph Time')



	# plt.show()
	cluster_center = []
	for point in kmeans.cluster_centers_[0]:
		cluster_center.append(round(point,2))
	return round(dist_from_center,2),round(max_dist,2),round(confidence,2),cluster_center


def generate_confidence_gaussian(train_data,status_data,login_data):
	print "<< train data >>",train_data
	print "<< status data >>",status_data
	print "<< len train data >>",len(train_data[0])
	train = numpy.array(train_data)
	status = numpy.array(status_data)

	gaussian = GaussianNB()
	gaussian.fit(train,status)
	pred_prob = gaussian.predict_proba([login_data])
	print "<< pred_prob >>",pred_prob
	convert_to_percent = lambda x: round(x*100,2)
	return map(convert_to_percent,pred_prob[0])




# def return_device_id_string(document):
# 	distance_string = ""
# 	for key in NAVIGATOR_KEY_LIST:
# 		distance_string += str(document.get("navigator",{}).get(key,""))+"|"
# 	return distance_string

# def return_fuzz_score_for_device(existing_device,current_device):
# 	existing_device_param_list = existing_device.split("|")
# 	current_device_param_list = current_device.split("|")
# 	complete_fuzz_score = 0
# 	for count,key in enumerate(NAVIGATOR_KEY_LIST):
# 		# print key,existing_device_param_list[count],current_device_param_list[count],NAVIGATOR_KEY_SCORE_MAP[key]
# 		complete_fuzz_score += fuzz.ratio(existing_device_param_list[count],current_device_param_list[count])*NAVIGATOR_KEY_SCORE_MAP[key]

# 	complete_fuzz_score = complete_fuzz_score/sum(NAVIGATOR_KEY_SCORE_MAP.values())
# 	complete_fuzz_score = round(complete_fuzz_score,2)
# 	return complete_fuzz_score

def return_device_id_string(document,channel="WEB"):
	global NAVIGATOR_KEY_LIST,NAVIGATOR_KEY_SCORE_MAP,MOBILE_WEB_NAVIGATOR_KEY_LIST,\
	MOBILE_WEB_NAVIGATOR_KEY_SCORE_MAP
	if channel == "MOBILE_WEB":
		print "found mobile web"
		NAVIGATOR_KEY_LIST = MOBILE_WEB_NAVIGATOR_KEY_LIST
	distance_string = ""
	for key in NAVIGATOR_KEY_LIST:
		distance_string += str(document.get("navigator",{}).get(key,""))+"|"
	return distance_string

def return_fuzz_score_for_device(existing_device,current_device,channel="WEB"):
	global NAVIGATOR_KEY_LIST,NAVIGATOR_KEY_SCORE_MAP,MOBILE_WEB_NAVIGATOR_KEY_LIST,\
	MOBILE_WEB_NAVIGATOR_KEY_SCORE_MAP
	existing_device_param_list = existing_device.split("|")
	current_device_param_list = current_device.split("|")
	complete_fuzz_score = 0
	per_key_match_score = {}
	if channel == "MOBILE_WEB":
		NAVIGATOR_KEY_LIST = MOBILE_WEB_NAVIGATOR_KEY_LIST
		NAVIGATOR_KEY_SCORE_MAP = MOBILE_WEB_NAVIGATOR_KEY_SCORE_MAP
	for count,key in enumerate(NAVIGATOR_KEY_LIST):
		print count,key
		per_key_match_score[key] = fuzz.ratio(existing_device_param_list[count],current_device_param_list[count])
		complete_fuzz_score += fuzz.ratio(existing_device_param_list[count],current_device_param_list[count])*NAVIGATOR_KEY_SCORE_MAP[key]
	complete_fuzz_score = complete_fuzz_score/sum(NAVIGATOR_KEY_SCORE_MAP.values())
	complete_fuzz_score = round(complete_fuzz_score,2)
	# print "user_agent info",httpagentparser.detect(current_device_param_list[19])
	return complete_fuzz_score,per_key_match_score,httpagentparser.detect(current_device_param_list[19])

# def return_user_agent_info(ua_string):
