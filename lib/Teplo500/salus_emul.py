import os.path
from Teplo500.utils import *

EMUL_DEVICES_ONLINE_FILE = "/local/fakes/devices_online.html"
EMUL_DEVICES_OFFLINE_FILE = "/local/fakes/devices_offline.html"

## args:
## return: 
##   true=success or false=failed
def emul_load_devices():

	file_path = app.home_path()
	if app.salus.emul_submode()==SalusConnect.EMUL_ONLINE:
		file_path += EMUL_DEVICES_ONLINE_FILE
	else:
		file_path += MUL_DEVICES_OFFLINE_FILE

	log_debug('emul_load_devices. file path='+file_path);

	if not os.path.isfile(file_path):
		log_error('No '+file_path+' file')
		return False

	try:
		with open (file_path, 'r') as fp:
			content = fp.read
	except:	
		log_error('Loaded '+file_path)
	
	return content
