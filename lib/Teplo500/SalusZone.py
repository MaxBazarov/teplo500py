from io import StringIO
from lxml import etree
import time

from teplo500.core import *
from teplo500.salus_emul import *
from teplo500 import SalusDevice

## PUBLIC CONSTANTS
MODE_UKNOWN = 0
MODE_AUTO = 1
MODE_OFF = 3
MODE_MAN = 4
MODE_ES = 5

MODES_TEXT={
	MODE_UKNOWN: '',
	MODE_AUTO: 'Auto/Mode',
	MODE_OFF: 'Off/Mode',
	MODE_MAN: 'Cust/Mode',
	MODE_ES: 'ES/Mode'
}


class SalusZone:

	## =================================== CONSTRUCTOR =========================== 
	## Arguments
	## device: SalusDevice or None
	def __init__(self, device, index=1,id=''):

		self.id = id
		self.index = index
		self.name = ''
		self.current_temp = None
		self.current_mode_temp = None

		self.mode = MODE_UKNOWN
		self.heating = False

		self.device = device ## can be None


	## =================================== PUBLIC GETTERS =========================== 	
	def mode(self):
		return self.mode
	
	def is_esm(self):
		return self.mode == MODE_ES
	
	## return text presention of current mode
	def mode_str(self):
		str = locstr(MODES_TEXT[self.mode])
		if self.mode != MODE_OFF and self.mode!=MODE_ES:
			str = str + ' ' + temp_to_str(self.current_mode_temp)
		return str;

    

	## =================================== PUBLIC SAVE/LOAD =========================== 
   	## arguments
	## data: object ref to client.data/devices[]/zones[]
	def load(self,data):

		self.id = data['id']
		self.index = data['index']
		self.updated = data['updated']
		self.name = data['name']
		self.current_temp = data['current_temp']
		self.current_mode_temp = data['current_mode_temp']
		self.mode = data['mode']
		self.heating = data['heating']

		log_debug('SalusZone: load: completed, index='+str(self.index))

		return True
	
	def get_data_for_save(self):

		data = {
			'id':self.id,
			'index':self.index,
			'updated':self.updated,
			'name':self.name,
			'current_temp':self.current_temp,
			'current_mode_temp':self.current_mode_temp,
			'mode':self.mode,
			'heating':self.heating
		}
		
		return data
	


	##  =================================== INTERNAL LOAD FROM HTML  =========================== 

	def load_from_dom(self,parent_node,li_node,is_new_zone):
	
		log_d = lambda msg: log_debug('SalusZone: load_from_dom(): '+msg)
		log_e = lambda msg: log_error('SalusZone: load_from_dom(): '+msg)

		index = self.index;
		
		img_node = li_node.xpath('img')[0]
		if img_node is None:
			return log_e('can not find li/img')

		zone_div_node = parent_node.xpath('div[@class="TabbedPanelsContent"]')[index-1]
		if zone_div_node is None:
			return log_e('can not find TabbedPanelsContent #'+str(index-1))
		
		log_d('load zone #'+str(index))
		
		if is_new_zone:
			self.name = img_node.attrib['alt']

		## get room temperature
		temp_room_node = zone_div_node.xpath('.//p[@id="current_room_tempZ'+str(index)+'"]')[0]
		if temp_room_node is None:
			return log_e('can not find room temperature for zone '+str(index))
		self.current_temp = float(temp_room_node.text);


		## get mode temperature
		temp_node = zone_div_node.xpath('.//p[@id="current_tempZ'+str(index)+'"]')[0]
		if temp_node is None:
			return log_e('can not find temperature for zone '+str(index))
		self.current_mode_temp = float(temp_node.text)

		## get heating on/off
		heating_nodes = zone_div_node.xpath('.//img[@id="CH'+str(index)+'onOff"][contains(@class,"display")]')
		self.heating = len(heating_nodes)>0
		
		## get energy save status
		es_enabled = False
		while True:
			node = zone_div_node.xpath('.//input[@name="esoption_submit"]')[0]
			if node is None:
				return log_e('can not find esoption_submit')

			if 'class' not in node.attrib:
				return log_e('can not find esoption_submit/@class');

			class_value = node.attrib['class']
			log_d('class = '+class_value)

			if class_value == 'esOff':
				es_enabled = False
			elif class_value == 'esOn':
				es_enabled = True
			else:	
				return log_e('can not understand esoption_submit/@class='+class_value)

			break;


		##get mode		
		while True:
			mode_off_nodes = zone_div_node.xpath('.//p[@id="offButtonZ'+str(index)+'"][contains(@class,"set")]')
			if len(mode_off_nodes)>0:
				self.mode = MODE_OFF
				break;
			
			if es_enabled:
				self.mode = MODE_ES
				break
			
			mode_man_nodes = zone_div_node.xpath('.//p[contains(@class,"heatingNote")][contains(@class,"heatingMan")]')
			if len(mode_man_nodes)>0:
				self.mode = MODE_MAN
				break
				
			mode_auto_nodes = zone_div_node.xpath('.//p[contains(@class,"heatingNote")][contains(@class,"heatingAuto")]')
			if len(mode_auto_nodes)>0:
				self.mode = MODE_AUTO
				break;
			
			return log_e('can not understand mode for zone '+str(index))
		
		
		## get current auto program
		##self.load_autotemp_from_dom($xpath,$zone_div_node);

		log_ok('[ZONE #'+str(self.index)+'] Temp '+temp_to_str(self.current_temp)+choose(self.heating,'[HEATING]','')+' Mode Temp '+temp_to_str(self.current_mode_temp))	

		## touch last updated time
		self.updated = int(time.time())
		
		return True


	def _load_autotemp_from_dom(self,zone_div_node):
	
		
		node = zone_div_node.find('.//p[@class="IT500programs"]/input[contains(@class,"IT500programFieldTemp")][contains(@class,"active")]')

		if node is None:
			return False
		
		temp = node.attrib['value']
		if temp is None:
			log_error('SalusZone: load_autotemp_from_dom(): can not find IT500programFieldTemp/@value')
			return False
		
		self.current_mode_temp = temp.split(' ',2)[0]

		return True
	
