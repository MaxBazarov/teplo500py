from Teplo500.utils import *
from Teplo500.salus_emul import *
from Teplo500 import SalusZone, SalusDevice, SalusClient

## PUBLIC CONSTANTS
PUBLIC_URL = 'https://salus-it500.com/public/'
START_URL = 'https://salus-it500.com';
LOGIN_URL= 'https://salus-it500.com/public/login.php'
DEVICES_URL = 'https://salus-it500.com/public/devices.php'
RENAME_DEVICE_URL = 'https://salus-it500.com/includes/rename.php'
SET_URL = 'https://salus-it500.com/includes/set.php'

MODE_REAL = 1
MODE_EMUL = 2 
MODE_CMD_HELP = 3

EMUL_ONLINE = 1 
EMUL_OFFLINE = 2

class SalusConnect:

	def __init__(self):
		## public
		self.clients = [] ## array of SalusClient

		## private		
		self._mode = MODE_REAL;
		self._emul_submode = EMUL_ONLINE;
	
	 
	## GETTERS
	def is_real_mode(self):
		return self._mode==MODE_REAL

	def is_emul_mode(self):
		return self._mode==MODE_EMUL

	def mode(self):
		return self._mode
	
	def emul_submode(self):
		return self._emul_submode

	def set_mode(self, mode):
		self._mode = mode

	def set_emul_submode(self, emul_submode):
		self._emul_submode = emul_submode
	
	def create_load_clients(self):			
		## load list of clients
		client_ids = self._load_client_list()
		if client_ids is None:
			return False;
		
		## load every client
		self.clients = []
		for client_id in client_ids:
			client = SalusClient.Factory_CreateAndLoad(client_id)
			if client is None:
				log_error('SalusConnect: run: can create client with id"'+client_id+'"')
				continue
			
			self.clients.append(client)
		
		return True
	
	def save_clients_data(self):
		result = True

		for client in self.clients:
			if not client.save_data():
				result = log_error('SalusConnect: save_clients: error')
				continue			
		
		return result
	

	def update_clients_from_site(self, force=False):
		result = True

		for client in self.clients:
			log_debug('SalusConnect: update_clients_from_site: client='+client.id)

			if not force and not client.is_updated_required():
				log_debug('SalusConnect: update_clients_from_site: skip updating')
				continue

			if not client.update_from_site():
				result = log_error('SalusConnect: update_clients_from_site: can not update_from_site')
				continue
			

			if not client.save_history():
				result = log_error('SalusConnect: update_clients_from_site: can save_history')
				continue
						
			if not client.run_alerts():
				log_error('SalusConnect: update_clients_from_site: can not run alerts')
			

			if not client.save_data():
				result = log_error('SalusConnect: update_clients_from_site: error');
				continue
					
		
		return result
	
	
	# result: array of file names  or false 
	def _load_client_list(self):
		
		try:
			import os
			files_raw = os.listdir(app.clients_folder())
		except:
			log_error('SalusConnect: _load_client_list: can not scan dir "'+app.clients_folder()+'"')
			return None

		return list(filter(lambda x: '@' in x,files_raw))
