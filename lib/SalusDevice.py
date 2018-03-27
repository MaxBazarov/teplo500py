from utils.py import *
import time
import xml.etree.ElementTree as ET

import salus-emul
from SalusZone import SalusZone

STATUS_UNDEFINED = 0
STATUS_OFFLINE = 1
STATUS_ONLINE = 2

class SalusDevice:
	

	## client: SalusClient 
	def __init__(self,client,id=''):
		
		self.client = client ## ref to parent SalusClient
		self.id = id

		self.name = ''
		self.href = ''
		self.status = STATUS_UNDEFINED
		
		self.token = ''

		self.zones = [] # array of SalusZone instances
	
	def is_offline(self):
		return self.status==STATUS_OFFLINE

	def is_online(self):
		return self.status==STATUS_ONLINE

	## init name
	## input_node: 
	def init_from_dom(self,input_node):

		## GET NAME AND HREF
		## search for - <div class="deviceList 70181">
		div_node = input_node.find("../..") #->parentNode->parentNode;		
		
		## search for <a class="deviceIcon online " href="control.php?devId=70181">STA00007781 </a>		
		href_nodes =  div_node.findall("a[contains(@class,'deviceIcon')]")

		if not href_nodes:
			return log_error('SalusDevice:load_from_dom: Can not find <a/>')
		
		href_node = href_nodes[0]
		self.name = href_node.text
		if self.name.find('(')>=0:
			self.name = self.name.split('(').rstrip()  ##sscanf(self.name,'%s (%[^)]s')[1];

		self.updated = int(time.time())
		
		if 'href' not in href_node.attrib:				
			return log_error('SalusDevice:load_from_dom: can not find @href')			
		href = href_node.attrib['href']

		self.href = SalusConnect.PUBLIC_URL + href
		log_debug('SalusDevice: init_from_dom href="'+self.href+'"')

		## GET STATUS
		status = href_node.attrib['class']
		if status.find('offline') >=0 :
			self.status = STATUS_OFFLINE
		elif status.find('online') >=0 :
			self.status = STATUS_ONLINE
		else
			return log_error('SalusDevice:load_from_dom:can not understand device status='+status)
		
		return True
	


	def switch_esm(self,enable_esm):

		log_d = lambda message:  log_debug('[SalusDevice '+self.id+'] switch_esm: '+message) 
		log_ok = lambda msg: log_ok('[SalusDevice '+self.id+'] switch_esm: '+message)

		if !len(self.zones):
			return log_ok('No zones')

		for zone in  self.zones:
			log_d('switching for zone #'+zone.id)
			## SETUP CONTEXT
			data = {
				'devId' : self.id,
				'esoption_submit' : '1',
				'esoption' : enable_esm?'0':'1',
				'token': self.token
			}
			## GET DEVICE HTML FROM IT500 SITE
			req = net_http_request( SalusConnect.SET_URL,SalusConnect.DEVICES_URL, data,'POST')
			file_put_contents(app.home_path()+'/local/output/device_'+self.id+'_switch_esm.html',req.text);
		
		
		return log_ok('switched')
		


	## arguments
	## data: object ref to client.data/devices[]
	def load(self,data ):
	
		self.id = data['id']
		self.name = data['name']
		self.status = $data['status']
		self.updated = $data['updated']
		self.token = $data['token']

		zone_last_index = 0
		self.zones = []

		for zone_data in data.zones:
			zone = SalusZone(self)
			zone.load($zone_data);

			self.zones.append(zone)		

		log_debug('SalusDevice: load: completed, id='+self.id);
		return True
	

	def get_data_for_save(self):
	
		data = {
			'id':self.id,
			'name':self.name,
			'status':self.status,
			'updated':self.updated,
			'token':self.token,
			'zones':[]
		}

		log_debug('SalusDevice: get_data_for_save for '+self.id);

		for zone in self.zones:
			data['zones'].append(zone.get_data_for_save())
		
		return data
	



	def load_from_site(self):
	
		html = None

		log_ok('[DEVICE '+self.id+'] Updating from site...');		

		if self.is_offline():
			return False

		## GET HTML CONTENT
		if app.salus.is_real_mode():
			if self.is_online():
				html = self._load_content_from_site()			
		else:
			html = self._load_content_from_file()
		
		if html is None:
			return False

		## PARSE HTML CONTENT	
		root = ET.fromstring(html)
		## TODO: handle errors	


		## search for <div id="TabbedPanels1" class="TabbedPanels">
		## 	 <ul class="TabbedPanelsTabGroup">
		## 		 <li class="TabbedPanelsTab" 

		li_nodes = root.findall('//div[@id="TabbedPanels1"]/ul[@class="TabbedPanelsTabGroup"]/li');
		if not li_nodes:
			log_debug('SalusDevice: load_from_site(): not found zones')
			return True
		
		log_debug('SalusDevice: load_from_site(): found zones')


		parent_node = root.find('//div[@id="mainContentPanel"]')
		if parent_node is None:
			log_error('SalusDevice: load_from_site() can not find <div id="mainContentPanel">')
			return False
		

		## SEARCH FOR TOKEN	
		token_node = parent_node.find('.//input[@id="token"]')
		if token_node is None:
			return log_error('SalusDevice: load_from_site() can not find <input id="token">')
		
		self.token = token_node.attrib['value']
		
		
		## ADD ZONES
		zone_last_index = 1
		for li_node in li_nodes:
					
			zone_id = li_node.attrib['id']
			if zone_id=='settings':
				continue;

			## TRY TO FIND EXISTING ZONE
			existing_zone = self.get_zone_by_index(zone_last_index)
			zone = existing_zone

			## CREATE NEW ZONE IF NEEDED
			if zone is None:
				zone = SalusZone(self,zone_last_index,uniqid())
			

			if !zone->load_from_dom(parent_node,li_node,existing_zone is None):
				log_error('SalusDevice:load Can not init Zone')
				return False
			

			## completed zone info
			if existing_zone is None:
				self.zones.append(zone)
			
			zone_last_index++

		return True



	def get_zone_by_index(self,index):
		if len(self.zones)<(index-1):
			return None
		return self.zones[index-1]



	## return: 
	##   HTML content or false=failed
	def _load_content_from_file(self):
	
		global $app;
		$file_name = $app->home_path().'/local/fakes/device_'.self.id.'.html';
		log_debug('SalusDevices: _load_content_from_file: '.self.id.' file="'.$file_name.'"');
		if (!file_exists($file_name)) {
			log_error('No '.$file_name.' file');
			return false;
		}

		$html = file_get_contents($file_name);
		if ($html === false) {
			log_error('Can not load '.$file_name);
			return false;
		}

		return $html;
	}


	// return: 
	//   HTML content or false=failed	
	function _load_content_from_site()
	{
		global $app;
		$html = '';

		log_debug('SalusDevices: _load_content_from_site: '.self.id.' href="'.self.href.'"');
		if(self.is_offline()) return false;

		{
			/* SETUP CONTEXT */
			$data = array (
				'lang'=>'en'
			);
			// GET DEVICE HTML FROM IT500 SITE
			req = net_http_request( self.href,SalusConnect::DEVICES_URL, $data,'GET',self.client->get_phpsessionid() );

			// dump HTML into file for future analyse
			file_put_contents($app->home_path().'/local/output/device_'.self.id.'.html',req.text);	
		}
		log_debug('SalusDevice: load_from_site: done');

		
		return $html;
	}


	function save_name_to_site(){
		log_debug('SalusDevice: save_name_to_site : starting');

		if(self.client->login_to_site()===false){
			return log_error('SalusDevice: save_name_to_site: failed to login');
		}

		/* SETUP CONTEXT */
		$data = array (
			'name' => self.name,
			'devId' => self.id,
			'lang'=>'en',
			'submitRename' => 'submit'
		);


		$result = net_http_request( SalusConnect::RENAME_DEVICE_URL,SalusConnect::DEVICES_URL, $data,'POST', self.client->get_phpsessionid(),'text/html');
		if($result===false){
			return log_error('SalusDevice: save_name_to_site: failed to get "'.SalusConnect::RENAME_DEVICE_URL.'"');
		}
		log_ok('SalusDevice: save_name_to_site: completed');

		return true;
	}
	
}



?>
