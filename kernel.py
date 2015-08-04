# coding: UTF-8
__author__ = 'Xiaolong Shen @ NEXD'

import sys
import os
from numpy import *
from sklearn.externals import joblib
# import imp
import time

sys.path.append('./RefCode/')

from loadfile import LoadWifiData
from ClassificationUtility import *
from sdk_utility import SDKUtility
from NB_Classification_Class import *


class AeonUtility(SDKUtility):
	"""
	Including Utility Functions for Aeon Usage

	DataStorage Content:
		self.wp_filepath = wp_filepath
		self.wifi_filepath = wifi_filepath
		self.wifi_list = wifi_list
		self.wp_pos = wp_pos
		self.wp_ind = wp_ind
		self.wifi_matrix = wifi_matrix

	"""
	def __init__(self):
		SDKUtility.__init__(self)
		self.loader = LoadWifiData()
		self.map_ratio = 10

	def load_wifi(self, wp_path, wifi_path, ref_list=[]):
		if ref_list:
			wifi = self.loader.extract_with_ref(wp_path, wifi_path, ref_list)
		else:
			wifi = self.loader.extract(wp_path, wifi_path)
		return wifi

	def extract_aeon(self, wifi_path, ref_list):
		file_list = os.listdir(wifi_path)
		route = []
		for fn in file_list:
			if 'journal' in fn:
				continue
			self.logger.debug("File %s is processed" % fn)
			data = self.extract_wifi(os.path.join(wifi_path,fn), ref_list)
			route += data
		return route

	def accuracy(self, res, test_pos, train_pos):
		RMSE = []
		for i,n in enumerate(res):
			pos_res = array(train_pos[n]);
			pos_tar = array(test_pos[i]);
			pos_diff = pos_res
			se = sqrt(((pos_tar - pos_diff) ** 2).sum()) / self.map_ratio
			RMSE.append(se)
		return RMSE

	def pos_weighted(self, w_arr, cls_pos):
		t_pos = zeros(array(cls_pos[0]).shape)
		for i, w in enumerate(w_arr):
			t_pos += array(cls_pos[i]) * w
		t_pos = t_pos / w_arr.sum()
		return t_pos

	def accuracy_proba(self, res, test_pos, train_pos):
		RMSE = []
		for n in range(res.shape[0]):
			w_arr = res[n,:]
			pos_res = self.pos_weighted(w_arr, train_pos)
			pos_tar = test_pos[n]
			se = sqrt(((pos_tar - pos_res) ** 2).sum()) / self.map_ratio
			RMSE.append(se)
		return RMSE

	def res_to_coord(self, res, train_pos, proba=False):
		# print res
		pos = []
		for x_res in res:
			if proba:
				pos_res = self.pos_weighted(x_res, train_pos)
			else:
				pos_res = array(train_pos[x_res])
			pos.append(pos_res)
		return pos

class AeonKernel(NBClassification):
	"""

	"""
	def __init__(self):
		NBClassification.__init__(self)
		# clf is the classifier trained out
		self.clf = None
		self.util = AeonUtility()

	def train(self, train_data, train_tar):
		self.clf = self.learn_clf(train_data, train_tar)

	def save(self, save_path = 'Aeon_Adaboost_Classifier.pkl'):
		# savez(save_path, clf=self.clf)
		joblib.dump(self.clf, save_path, compress=9)

	def load_clf(self, load_path = 'Aeon_Adaboost_Classifier.pkl'):
		ref = joblib.load(load_path)
		self.clf = ref

	def test(self, test_data, proba=False):
		if proba:
			res = self.clf.predict_proba(test_data)
		else:
			res = self.clf.predict(test_data)
		return res

	def validate_test_accuracy(self, test_data, test_pos, train_pos):
		res = self.test(test_data)
		RMSE = self.util.accuracy(res, test_pos, train_pos)
		print "RMSE:%s\n Average Mean Error: %s" %(RMSE, array(RMSE).mean())
		return array(RMSE).mean()

	def validate_test_accuracy_proba(self, test_data, test_pos, train_pos):
		res_proba = self.test(test_data, True)
		RMSE = self.util.accuracy_proba(res_proba, test_pos, train_pos);
		print "RMSE:%s\n Average Mean Error: %s" %(RMSE, array(RMSE).mean())
		return array(RMSE).mean()


class Aeon(AeonKernel):
	def __init__(self):
		AeonKernel.__init__(self)
		self.wifi_list = None
		self.wp_pos = None
		self.data = None

	def load_data(self, data_path):
		ref = load(data_path)
		self.wifi_list = ref['wifi_list']
		self.wp_pos = ref['wp_pos']
		self.data = ref['all_data']

	def load_config(self, clf_path, data_path):
		self.load_clf(clf_path)
		self.load_data(data_path)

	def locator(self, data):
		res = self.test(data)
		return self.util.res_to_coord(res, self.wp_pos)

	def process_route(self, route_path):
		# print self.wifi_list
		self.util.logger.debug("The Route Input is %s" % route_path)
		route = self.util.extract_aeon(route_path, self.wifi_list)
		res = {}
		res_cred = {}
		for dp in route:
			# print "data property -- count: %s, miss_count: %s" %(dp.total_mac_count, dp.miss_mac_count)
			for x in self.locator(dp.wifi_matrix):
				# print x
				res[dp.timestamp] = {}
				res[dp.timestamp]['user'] = dp.user
				res[dp.timestamp]['post'] = x
				res_cred[dp.timestamp] = [dp.total_mac_count, dp.miss_mac_count]
		return res, res_cred

	def output_format(self, res, res_cred):
		f = open('res_record.xml','w')
		bid = '10107993'
		fid = '101079930001'
		res_key = list(res.keys())
		res_key.sort()
		st = time.strftime("%Y%m%d%H%M%S",time.localtime(res_key[0]*1e-3))
		ed = time.strftime("%Y%m%d%H%M%S",time.localtime(res_key[-1]*1e-3))
		f.write('<?xml version="1.0" encoding="GB2312"?>\n')
		f.write('<recode bid="%s" floorID="%s" startTime="%s" endTime="%s">\n' % (bid, fid, st, ed))
		f.write('\t<LocationPoints>\n')
		for x in res_key:
			cred = res_cred[x]
			t = time.localtime(x * 1e-3)
			nt = time.strftime("%Y%m%d%H%M%S", t)
			if cred[0]<5:
				continue
			if (cred[0]-cred[1]) / cred[0] < 0.7:
				continue;
			f.write('\t\t<LoctP timestamp="%s" posX="%s" posY="%s"/>\n' % (nt, res[x][0], res[x][1]))
		f.write('\t</LocationPoints>\n')
		f.write('\t<RealPoints id="1">\n')
		f.write('\t\t<RealP timestamp="%s" posX="%s" posY="%s"/>\n' % (st, "0.0", "0.0"))
		f.write('\t\t<RealP timestamp="%s" posX="%s" posY="%s"/>\n' % (ed, "0.0", "0.0"))
		f.write('\t</RealPoints>\n')
		f.write('</recode>\n')
		f.close()
