__author__ = 'Xiaolong Shen @ Nexd Tech'
from ClassificationUtility import *
from sklearn.naive_bayes import GaussianNB
import time

class NBClassification():

	"""
	Dumped Method:


	# def run_with_nothing(self, train_data, test_data, display=True):
	# 	clf = self.learn_clf(train_input, train_tar, display)
	# 	res, RMSE = self.validate_clf(clf, test_input, test_tar, raw_coord, display)
	#
	# 	return clf, res, RMSE
	#
	# def run_with_resample(self, train_data, test_data, display=True):
	# 	# Resample Data to Acuumulate data
	#
	# 	test_input = self.util.resample_data(test_input)
	#
	# 	clf = self.learn_clf(train_input, train_tar, display)
	# 	res, RMSE = self.validate_clf(clf, test_input, test_tar, raw_coord, display)
	#
	# 	return clf, res, RMSE
	#
	# def run_with_weight(self, train_data, test_data, display=True):
	# 	clf = self.learn_clf(train_input, train_tar, display)
	# 	res, RMSE = self.validate_clf_with_proba(clf, test_input, test_tar, raw_coord, display)
	#
	# 	return clf, res, RMSE




	"""




	def __init__(self):
		self.util = ClassificationUtility()
		self.DT_depth = 10
		self.num_estimator = 200
		self.learning_rate = 1

	def init_classifier(self):
		clf = GaussianNB()
		return clf

	def train_clf(self, clf, train_data, train_tar, display=True):
		clf.fit(train_data, train_tar)
		if display:
			st = time.time()
			clf.predict(train_data)
			ed = time.time()

			res_score = clf.score(train_data, train_tar)

			print "Score: %s" % res_score
			print "Time Cost: %s, Ave: %s" % (ed-st, (ed-st)/train_data.shape[0])
		return clf

	def test_clf(self, clf, test_data):
		pass

	def validate_clf(self, clf, test_data, test_tar, raw_coord, display=True):
		res = clf.predict(test_data)
		RMSE = self.util.accuracy(res, test_tar, raw_coord)
		if display:
			print "RMSE: %s, Var: %s, MAX: %s" % (mean(RMSE), std(RMSE), max(RMSE))
			print RMSE
		return res, RMSE

	def validate_clf_with_proba(self, clf, test_data, test_tar, raw_coord, display=True):
		res_proba = clf.predict_proba(test_data)
		RMSE = self.util.accuracy_weighted(res_proba, test_tar, raw_coord)
		if display:
			print "RMSE: %s, Var: %s, MAX: %s" % (mean(RMSE), std(RMSE), max(RMSE))
			print RMSE
		return res_proba, RMSE

	def learn_clf(self, train_data, train_tar, display=True):
		clf = self.init_classifier()
		clf = self.train_clf(clf, train_data, train_tar, display)
		return clf

	def run_ble(self, train_data, test_data, display=True, resample=True, weight=True):
		train_input = train_data.mat_res.mat
		train_tar = train_data.mat_res.cls
		test_input = test_data.mat_res.mat
		test_tar = test_data.mat_res.cls
		raw_coord = train_data.mat_res.cls_coord

		if resample:
			test_input = self.util.resample_data(test_input)

		if weight:
			clf = self.learn_clf(train_input, train_tar, display)
			res, RMSE = self.validate_clf_with_proba(clf, test_input, test_tar, raw_coord, display)

			return clf, res, RMSE
		else:
			clf = self.learn_clf(train_input, train_tar, display)
			res, RMSE = self.validate_clf(clf, test_input, test_tar, raw_coord, display)
			return clf, res, RMSE




