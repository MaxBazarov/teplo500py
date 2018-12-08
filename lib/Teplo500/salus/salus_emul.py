import os.path
from teplo500.core import *
from teplo500.salus import salus_connect

EMUL_DEVICES_ONLINE_FILE = "/local/fakes/devices_online.html"
EMUL_DEVICES_OFFLINE_FILE = "/local/fakes/devices_offline.html"

## args:
## return: 
##   true=success or false=failed
def emul_load_devices():

	file_path = get_app().home_path()
	if get_app().salus.emul_submode()==salus_connect.EMUL_ONLINE:
		file_path += salus_connect.EMUL_DEVICES_ONLINE_FILE
	else:
		file_path += salus_connect.MUL_DEVICES_OFFLINE_FILE

	log_debug('emul_load_devices. file path='+file_path);

	if not os.path.isfile(file_path):
		log_error('No '+file_path+' file')
		return False

	try:
		with open (file_path, 'r') as fp:
			content = fp.read()
	except:	
		log_error('Loaded '+file_path)
	
	return content
