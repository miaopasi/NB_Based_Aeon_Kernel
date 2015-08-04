__author__ = 'Xiaolong Shen sxl@nexdtech.com'

from numpy import *
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from load_BLE_data import *
import time
from math import *


class ClassificationUtility:

	def __init__(self):
		self.map_ratio = 133.0
		self.stack_depth = 3
		pass

	def accuracy(self, res_cls, cls, cls_pos):
		RMSE = []
		for n in range(len(res_cls)):
			cls_res = res_cls[n]
			cls_tar = cls[n]
			pos_res = array(cls_pos[cls_res])
			pos_tar = array(cls_pos[cls_tar])
			pos_diff = pos_res
			se = sqrt(((pos_tar - pos_diff) ** 2).sum()) / self.map_ratio
			RMSE.append(se)
		return RMSE

	def stack_data(self, mat):
		depth = mat.shape[0]
		length = mat.shape[1]
		# print "LENGTH: %s, DEPTH: %s" %(length, depth)
		arr = zeros((1, length))
		count = zeros((1, length))
		for i in range(depth):
			for j in range(length):
				if mat[i, j] == 0:
					continue
				arr[0, j] += mat[i, j]
				count[0, j] += 1
		for j in range(length):
			if not count[0, j] == 0:
				arr[0, j] = float(arr[0, j]) / float(count[0, j])
		return arr

	def resample_data(self, data_mat):
		print data_mat.shape
		re_data_mat = empty_like(data_mat)

		for i in range(data_mat.shape[0]):
			arr = self.stack_data(data_mat[max(0, i - self.stack_depth):i + 1, :])
			re_data_mat[i, :] = arr[0]
		return re_data_mat

	def pos_weighted(self, w_arr, cls_pos):
		t_pos = zeros(array(cls_pos[0]).shape)
		for i, w in enumerate(w_arr):
			t_pos += array(cls_pos[i]) * w
		t_pos = t_pos / w_arr.sum()
		return t_pos


	def accuracy_weighted(self, res_proba, cls, cls_pos):
		RMSE = []
		for n in range(res_proba.shape[0]):
			w_arr = res_proba[n,:]
			pos_res = self.pos_weighted(w_arr, cls_pos)
			pos_tar = cls_pos[cls[n]]
			se = sqrt(((pos_tar - pos_res) ** 2).sum()) / self.map_ratio
			RMSE.append(se)
		return RMSE



