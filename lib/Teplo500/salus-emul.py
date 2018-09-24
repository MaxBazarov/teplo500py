import os.path

from utils.py import *

EMUL_DEVICES_ONLINE_FILE = "/local/fakes/devices_online.html"
EMUL_DEVICES_OFFLINE_FILE = "/local/fakes/devices_offline.html"


## args:
## return: 
##   true=success or false=failed
def emul_load_devices():

	file_path = app.home_path()+(app.salus.emul_submode()==SalusConnect.EMUL_ONLINE? EMUL_DEVICES_ONLINE_FILE: EMUL_DEVICES_OFFLINE_FILE)
	log_debug('emul_load_devices. file path='+file_path);

	if not os.path.isfile(file_path):
		log_error('No '+file_path+' file')
		return False

	try:
		with open (file_path, 'r') as fp:
			content = fp.read

	log_ok('Loaded '+file_path)
	
	return content
