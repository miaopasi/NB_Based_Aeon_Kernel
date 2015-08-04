__author__ = 'admin'

from kernel import *
import time

au = AeonUtility();
train = au.load_wifi('./Data/Training/data_new.wp', './Data/Training/data_new.wifi')
savez('Aeon_Base_Data.npz', wifi_list=train.wifi_list, wp_pos=train.wp_pos, all_data=train)
test = au.load_wifi('./Data/Training/data.wp', './Data/Training/data.wifi', train.wifi_list)

print test.wifi_matrix.shape
print test.wp_pos.shape

print "> Loading Finished"
ak = AeonKernel();
ak.train(train.wifi_matrix, arange(train.wifi_matrix.shape[0]))
print "> Training Finished"
ak.save()
print "> Saved"
ak.load_clf()
# print "> Load In"

`
st = time.time()
ak.validate_test_accuracy_proba(test.wifi_matrix, test.wp_pos, train.wp_pos)
ed = time.time()
print "> Validation Done"
print "> Time Comsumption for Test : %s, Average Time Comsumption : %s" %(ed-st, float(ed-st)/test.wifi_matrix.shape[0])

