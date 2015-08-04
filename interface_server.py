__author__ = 'Xiaolong Shen @ NexdTech'

from kernel import *
import time



def interface_server(file_path):
	"""
	:input_param: file_path for one collection
	:output_param: list of dictionaries
		dictionary:
			user_id: special id for user, STRING
			post_x: x coordinate of position, DOUBLE
			post_y: y coordinate of position, DOUBLE
			post_cred: credibility of position, DOUBLE
			timestamp: the time when the position is given, long
	"""
	ae = Aeon()
	ae.load_config('Aeon_Adaboost_Classifier.pkl', 'Aeon_Base_Data.npz')
	interface_res = []
	res, res_cred = ae.process_route(file_path)
	res_key = list(res.keys())
	for time_key in res_key:
		if res_cred[time_key][0] < 5:
			continue
		temp_result = {'user_id': str(res[time_key]['user']), 'post_x': float(res[time_key]['post'][0]),
		               'post_y': float(res[time_key]['post'][1]), 'time_stamp': long(time_key),
		               'post_cred': float((res_cred[time_key][0] - res_cred[time_key][1]) / res_cred[time_key][0])}
		ae.util.logger.debug("This Is The Result at Time: %s, The Res is %s" % (time_key, temp_result))
		interface_res.append(temp_result)
	return interface_res

interface_server('../Raw_Data/Collect_File_Type/test')