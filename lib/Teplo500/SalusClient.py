## Standard Libs
from email.utils import parseaddr
import cgi, os, time
from io import StringIO
from lxml import etree
from datetime import date

## Own Libs
from Teplo500.utils import *
from Teplo500.Alert import *
from Teplo500.SalusDevice import *
import Teplo500.salus_emul
import Teplo500.SalusHistoryHelper
import Teplo500.Emailer


## args:
##	client_id : email address
## result
##  ref to SalusClient or False

def SalusClient_CreateAndLoad(client_id):

	log_debug('CreateAndLoad: creating client '+client_id+'...')

	client_id =client_id.strip()
	
	if client_id=='':
		return log_error('CreateAndLoad: construct: ID undefined')
	

	client = SalusClient(client_id)
	
	if not client.load():
		return log_error('CreateAndLoad: run: can not load client')
	

	log_debug('CreateAndLoad: created client '+client_id)

	return client


## args:
##	email : email address
##	pswd : password
## result
##  ref to SalusClient or False

def SalusClient_CreateAndRegister(name,email,password):
	log_debug('Factory_CreateAndRegister: creating client')

	client = SalusClient(email)

	if not client._set_name(name):
	 return False
	if not client._set_login(email,password):
	 return False

	if not client.register():
		return log_error('Factory_CreateAndRegister: run: can not register new client')
	
	if not client.load():
		return log_error('Factory_CreateAndRegister: run: can not load client')


	log_debug('Factory_CreateAndRegister: created client '+client.id)

	return client



class SalusClient:

	def __init__(self,id):   
		## TODO: escape id
    	##id = cgi.escape(id.strip(),True)
    	
    	# PUBLIC
		self.id = id
		self.name = ''
		self.alert_email = ''
		self.config = {}
		self.devices = [] ## list of {SalusDevice}
		self.data_updated_time = 0 ## time of last data update

		## PRIVATE 
		self.login_email = ''
		self.login_password = ''
		self.PHPSESSID = ''
		
	## check do we need to update it right now or not?
	def is_updated_required(self):
		if self.data_updated_time==0:
			return True

		conf_period = self.get_auto_update()
		if conf_period==0: 
			return True


		now_period =  datetime.now() - self.data_updated_time

		return now_period >= conf_period

	def update_from_site(self):
		log_ok('[CLIENT '+self.id+'] Updating from site...')

		if not self._update_device_list_from_site():
			return log_error('SalusClient: run: can not init devices')
		
		if not self._load_devices_from_site():
			return log_error('SalusClient: run: can not load devices')		
		
		return True
	

	def switch_esm(self, enable_esm):
		log_d = lambda message: log_debug('[CLIENT '+self.id+'] switch_esm(): '+message)
		log_e = lambda message: log_error('[CLIENT '+self.id+'] switch_esm(): '+message)
		log_ok = lambda message: log_ok('[CLIENT '+self.id+'] switch_esm(): '+message)

		log_d('switching into '+enable_esm)


		for device in self.devices:
			if not device.switch_esm(enable_esm):
				return log_e('failed to switch')

		log_ok('switched ESM successfully')

		if not self.update_from_site():
			return log_e('failed to update data')
		if not self.save_updated():
			return log_e('failed to save updated data')

		return True
	

	def get_auto_update(self):		
		if 'auto_update' in self.config:
			return self.config['auto_update']
		else:
			return get_app().config['defaults.auto_update']
		
	def get_auto_upday_txt(self):
		period = self.get_auto_update()
		if period==0:
			return locstr('Off')

		if period<3600:
			return (period / 60)+' '+locstr('minute(s)/timediff')
		elif period<86400:
			return (period / 3600)+' '+locstr('hour(s)/timediff')
		else:
			return (period / 86400)+' '+locstr('day(s)/timediff')
	

	def validate_password(self,pswd):
		return pswd == self.login_password
	

	def run_alerts(self):
	
		## load old alert data
		data = self._load_json_config('alerts.data',True)
		if data is None:
			data = {
				'alerts':[]
			}			
		
		## iterate know alerts
		new_data = {
			'alerts':{}
		}

		for id in ALERT_IDS:
			
			if not(id in self.config['alerts']):
				continue

			conf = self.config['alerts'][id]
			if not conf['on']:
				continue

			log_debug('SalusClient: run_alerts: test alert'+id)

			existing_data = choose(id in data['alerts'],data['alerts'][id],{})

			alert = CreateAlert(id,conf,existing_data)
			if alert is None:
				return log_error('SalusClient: _run_zone_alert: can create Alert instance')	
			
			new_data['alerts'][id] = alert.test_client(self)
		

		## save new data
		if not self._save_json_config('alerts.data',new_data):			
			return log_error('SalusClient: run_alerts: can not save new data')
		
		return True
	

	## Load client, devices and zones date stored locally
	def load(self):
		
		## READ AUTH CONFIG
		auth_config = self._load_json_config('auth.conf')
		if auth_config is None:
			return log_error('SalusClient: load: can not load auth config')
			
		self.login_email = auth_config['email'];
		self.login_password = auth_config['key'];

		## READ MAIN CONFIG
		config = self._load_json_config('client.conf')
		if config is None:
			return log_error('SalusClient: load: can not load config')

		self.config = config
		self.alert_email = config['client']['alert_email']
		self.name = config['client']['name']

		## read existing data
		self.devices = []
		data = self._load_json_config('client.data',False)
		if data is not None:
			self.data_updated_time = data['time']
			for device_data in data['devices']:
				device = SalusDevice(self) 
				device.load(device_data)
				self.devices.append(device)

		return log_debug('SalusClient: load: completed')


	def register(self):
		## check client older for existing
		path = self.get_folder_path()

		if not os.path.exists(path):
			try:
				os.mkdir(path)
			except OSError as exc: 
				return log_error('SalusClient: register: can not create client folder "'+path+'"')				

			history_path = path + '/history'
			try:
				os.mkdir(history_path)
			except OSError as exc: 
				return log_error('SalusClient: register: can not create client history folder "'+history_path+'"')
				
		## init default config
		self.config = {
			'client':{
				'name':self.name,
				'alert_email':self.login_email
			},
			'alerts':get_app().config['default_alerts']
		}

		self.save_config()
		self.save_auth()
		self.save_data()

		return True
	


	def save_updated(self):
		if not self.save_history(): return False
		if not self.run_alerts(): return False
		if not self.save_data(): return False
		return True
	
	def save_auth(self):
	
		data = {
			'email':self.login_email,
			'key':self.login_password
		}

		if not self._save_json_config('auth.conf',data):
			return log_error('SalusClient: save_auth: can not save client auth')
		
		return True
	

	def save_config(self):	
		if not self._save_json_config('client.conf',self.config):
		 return log_error('SalusClient: save_config: failed')
		return True	


	def save_data(self):

		data = self.get_data_for_save()
		if not self._save_json_config('client.data',data):
			return log_eror('SalusClient: save: can not save client data')
		
		self.data_updated_time = data['time'];
				
		return True
	

	def get_data_for_save(self):
		return {
			'time':int(time.time()),
			'date':time.strftime('%y %m %d %H:%M:%S'),
			'devices':list(map(lambda device: device.get_data_for_save() ,self.devices))
		}	

	def save_history(self):
		return Teplo500.SalusHistoryHelper.save_client_history(self)
	

	def get_folder_path(self):
		return get_app().clients_folder()+'/'+self.id;


	def get_device_by_id(self,id):
		for dev in self.devices:
			if dev.id==id:
			 return dev
		
		return None
	
	def get_zone_by_id(self,id):
		for dev in self.devices:
			for zone in dev.zones:
				if zone.id==id:
					return zone
		return None
	

	##//////////////////////////////////////////////////////////// PRIVATE FUNCTIONS //////////////////////////////////////

	
	def _set_login(self,email,password):

		## cleanup arguments
		email = cgi.escape(email.strip(),True)
		password = cgi.escape(password.strip(),True)

		if '@' not in parseaddr(email)[1]:
			return False

		if password=='':
			return False

		## save
		self.login_email = email
		self.login_password = password;

		return True

	def _set_name(self,name):

		## cleanup arguments
		name = name.strip()
		
		if name=='':
			return False
		
		self.name = name
		
		return True
	

	##///////////////////////////////////////////// SAVE/LOAD CONFIGS ///////////////////////////////////////////////////////

	

	def _load_json_config(self, file_name, ignore_missing=False):

		path = self.get_folder_path()+'/'+file_name;
		if not os.path.exists(path):
			if ignore_missing:
				return {}
			else:
				log_error('SalusClient: _load_json_config: can not find file "'+path+'"')
				return None
		
		return load_json_config(path)
	
	def _save_json_config(self,file_name,config):
	
		path = self.get_folder_path()+'/'+file_name

		if not save_json_config(path,config):
			return log_error('SalusClient: _save_json_config: can not save config "'+file_name)
	
		return True


	##///////////////////////////////////////////// COMMUNICATION WITH SITE ///////////////////////////////////////////////////////


	## result: 
	##		True or False
	def login_to_site(self):
		salus = get_app().salus
	
		if not salus.is_real_mode():
			return True
	

		## GET FIRST COOKIE
		data = {
			'lang':'en'
		}
		req = net_http_request( salus.START_URL,salus.START_URL, data,'GET' )	
		self.PHPSESSID = req.cookies['PHPSESSID'] if 'PHPSESSID' in req.cookies else ''
		log_debug('login_to_site: PHPSESSID="'+self.PHPSESSID+'"')	

		## TRY LOGIN
		## SETUP CONTEXT 
		data = {
			'IDemail': self.login_email,
			'password': self.login_password,
			'lang': 'en',
			'login': 'Login'
		}

		req = net_http_request( salus.LOGIN_URL,salus.LOGIN_URL, data,'POST',self.PHPSESSID)
		if req is None or req.status_code!=200:
			log_error('SalusClient: login_to_site: failed to get "'+salus.LOGIN_URL+'"')
			return None

		return req


	## result: 
	##		True or False
	def _update_device_list_from_site(self):
			
		log_debug('SalusClient: _update_devices_from_site : started')

		req = self.login_to_site()
		if req is None:
			return log_error('SalusClient: _update_devices_from_site : failed  - can not ping')

		devices_html = '';

		if get_app().salus.is_real_mode():
			log_debug('SalusClient: _update_devices_from_site : loaded real data from site')			
			devices_html = req.text
			with open(get_app().home_path()+'/local/output/devices.html', 'w') as f:
				f.write(devices_html)
		elif get_app().salus.is_emul_mode():
			log_debug('SalusClient: _update_devices_from_site : load faked data from local file')
			devices_html = Teplo500.salus_emul.emul_load_devices()
		else:
			return log_error('salus_login: unknown app mode='+get_app().salus.mode())
		
		return self._parse_html_devices(devices_html)		


	def get_phpsessionid(self):
		return self.PHPSESSID

	## args
	##		devices_html: string
	## return: True=success or False=failed
	def _parse_html_devices(self,devices_html):
		log_d = lambda message:  log_debug('SalusClient: _parse_html_devices(): '+message) 

		log_d('starting...')

		parser = etree.HTMLParser()
		tree  = etree.parse(StringIO(devices_html), parser)
		
		## search for <input name="devId" type="hidden" value="70181"/>
		inputs_nodes = tree.xpath("//input[@name='devId']")

		if len(inputs_nodes)==0 : return log_error('salus_parse_devices: Can not find device definition in HTML')

		## ADD FOUND DEVICES
		for input_node in inputs_nodes:
			## GET ID	
			id = input_node.attrib['value']
			log_d('id='+id)
			
			## TRY TO FIND ALREADY EXISTING DEVICE
			existing_dev = self.get_device_by_id(id)
			dev = existing_dev;

			if not dev:
				dev = SalusDevice(self,id)		

			if not dev.init_from_dom(input_node): return log_error('salus_parse_devices: can not load device')

			## STORE NEW DEVICE
			if not existing_dev: array_push(self.devices,dev)		
		
		log_d('done')		

		return True
	

	def _load_devices_from_site(self):
		for dev in self.devices:
			if not dev.load_from_site():
				log_error('SalusClient: load_devices: can not load device #'+dev.id)
				return False
		return True
