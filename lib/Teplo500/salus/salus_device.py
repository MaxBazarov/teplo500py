import time
import os,os.path,sys
from io import StringIO
from lxml import etree

from teplo500.core import *
from teplo500.salus import salus_connect
from teplo500.salus import salus_zone

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
		salus = get_app().salus

		## GET NAME AND HREF
		## search for - <div class="deviceList 70181">
		div_node = input_node.xpath("../..")[0] ##->parentNode->parentNode;		

		## search for <a class="deviceIcon online " href="control.php?devId=70181">STA00007781 </a>		
		href_nodes =  div_node.xpath("a[contains(@class,'deviceIcon')]")

		if len(href_nodes)==0: return log_error('SalusDevice:load_from_dom: Can not find <a/>')
		
		href_node = href_nodes[0]
		self.name = href_node.text
		if self.name.find('(')>=0:
			self.name = self.name.split('(')[0].rstrip()  ##sscanf(self.name,'%s (%[^)]s')[1];

		self.updated = int(time.time())
		
		href = href_node.attrib['href']
		if href is None: return log_error('SalusDevice:load_from_dom: can not find @href')			
		
		self.href = salus.PUBLIC_URL + href
		log_debug('SalusDevice: init_from_dom href="'+self.href+'"')

		## GET STATUS
		status = href_node.attrib['class']
		if status is None: return log_error('SalusDevice:load_from_dom:can not find device status')

		if status.find('offline') >=0 :
			self.status = STATUS_OFFLINE
		elif status.find('online') >=0 :
			self.status = STATUS_ONLINE
		else:
			return log_error('SalusDevice:load_from_dom:can not understand device status='+status)
		
		return True
	


	def switch_esm(self,enable_esm):

		log_d = lambda msg: log_debug('[SalusDevice '+self.id+'] switch_esm: '+msg) 
		log_ok = lambda msg: log_ok('[SalusDevice '+self.id+'] switch_esm: '+msg)

		if not len(self.zones):
			return log_ok('No zones')

		for zone in  self.zones:
			log_d('switching for zone #'+zone.id)
			## SETUP CONTEXT
			data = {
				'devId' : self.id,
				'esoption_submit' : '1',
				'esoption' : choose(enable_esm,'0','1'),
				'token': self.token
			}
			## GET DEVICE HTML FROM IT500 SITE			
			req = net_http_request( get_app().salus.SET_URL,get_app().salus.DEVICES_URL, data,'POST')
			dump_file_name = get_app().home_path()+'/local/output/device_'+str(self.id)+'_switch_esm.html'
			with open(dump_file_name, 'w') as f:
				f.write(req.text)		
		
		return log_ok('switched')
		


	## arguments
	## data: object ref to client.data/devices[]
	def load(self,data ):
	
		self.id = data['id']
		self.name = data['name']
		self.status = data['status']
		self.updated = data['updated']
		self.token = data['token']

		zone_last_index = 0
		self.zones = []

		for zone_data in data['zones']:
			zone = salus_zone.SalusZone(self)
			zone.load(zone_data);

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
		if get_app().salus.is_real_mode():
			if self.is_online():
				html = self._load_content_from_site()			
		else:
			html = self._load_content_from_file()
		
		if html is None:
			return False

		## PARSE HTML CONTENT	
		parser = etree.HTMLParser()
		tree  = etree.parse(StringIO(html), parser)
		## TODO: handle errors	

		## search for <div id="TabbedPanels1" class="TabbedPanels">
		## 	 <ul class="TabbedPanelsTabGroup">
		## 		 <li class="TabbedPanelsTab" 

		li_nodes = tree.xpath('//div[@id="TabbedPanels1"]/ul[@class="TabbedPanelsTabGroup"]/li');
		if len(li_nodes)==0:
			log_debug('SalusDevice: load_from_site(): not found zones')
			return True
		
		log_debug('SalusDevice: load_from_site(): found zones')

		parent_node = tree.xpath('//div[@id="mainContentPanel"]')[0]
		if parent_node is None:
			log_error('SalusDevice: load_from_site() can not find <div id="mainContentPanel">')
			return False
		

		## SEARCH FOR TOKEN	
		token_node = parent_node.xpath('.//input[@id="token"]')[0]
		if token_node is None:
			return log_error('SalusDevice: load_from_site() can not find <input id="token">')
		
		self.token = token_node.attrib['value']
		
	
		## ADD ZONES
		zone_last_index = 1
		for li_node in li_nodes:
					
			if 'id' not in li_node.attrib:
				zone_id = 'zone1'
			else:
				zone_id = li_node.attrib['id']
				if zone_id=='settings':
					continue;

			## TRY TO FIND EXISTING ZONE
			existing_zone = self.get_zone_by_index(zone_last_index)
			zone = existing_zone

			## CREATE NEW ZONE IF NEEDED
			if zone is None:
				zone = salus_zone.SalusZone(self,zone_last_index,uniqid())
			

			if not zone.load_from_dom(parent_node,li_node,existing_zone is None):
				log_error('SalusDevice:load Can not init Zone')
				return False
			

			## completed zone info
			if existing_zone is None:
				self.zones.append(zone)
			
			zone_last_index+=1

		return True



	def get_zone_by_index(self,index):
		if len(self.zones)<(index-1):
			return None
		return self.zones[index-1]



	## return: 
	##   HTML content or false=failed
	def _load_content_from_file(self):
	
		file_name = get_app().home_path()+'/local/fakes/device_'+self.id+'.html'
		log_debug('SalusDevices: _load_content_from_file: '+self.id+' file="'+file_name+'"')
		if not os.path.exists(file_name):
			log_error('No '+file_name+' file')
			return False		
		
		fo = open(file_name,"r")
		html = fo.read()
		fo.close()

		return html
	


	## return: 
	##   HTML content or false=failed	
	def _load_content_from_site(self):
	
		html = '';

		log_debug('SalusDevices: _load_content_from_site: '+self.id+' href="'+self.href+'"')
		if self.is_offline():
		 return False

		
		##SETUP CONTEXT 
		data = {
			'lang':'en'
		}
		## GET DEVICE HTML FROM IT500 SITE
		req = net_http_request( self.href,get_app().salus.DEVICES_URL, data,'GET',self.client.get_phpsessionid() )

		## dump HTML into file for future analyse
		file_name = get_app().home_path()+'/local/output/device_'+self.id+'.html'
		fp = open(file_name, 'w')
		fp.write(req.text)
		fp.close()
		
		log_debug('SalusDevice: load_from_site: done')

		
		return req.text
	


	def save_name_to_site(self):
		log_debug('SalusDevice: save_name_to_site : starting');

		if not self.client.login_to_site():
			return log_error('SalusDevice: save_name_to_site: failed to login')
		

		## SETUP CONTEXT 
		data = {
			'name' : self.name,
			'devId' : self.id,
			'lang' : 'en',
			'submitRename' : 'submit'
		}

		req = net_http_request( get_app().salus.RENAME_DEVICE_URL,get_app().salus.DEVICES_URL, data,'POST', self.client.get_phpsessionid(),'text/html')

		if not req:
			return log_error('SalusDevice: save_name_to_site: failed to get "'+salus_connect.RENAME_DEVICE_URL+'"')
	
		log_ok('SalusDevice: save_name_to_site: completed')

		return True
	