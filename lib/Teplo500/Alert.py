from datetime import date
import time

from Teplo500.core import *
import Teplo500.Emailer

ALERT_IDS = ['low_temp']

class AbstractAlert:

	def __init__(self,id,conf,data):   	
		self.id = id
		self.conf = conf ## object with client/config.conf/alerts/{} content
		self.data = data ## array with client/alerts.data content
		self.exec_time = 0

	## SalusClient client
	## SalusDevice device
	## SalusZone zone
	def test_client_zone(self,client, device, zone):
		return False

	## result: 
	##{
    ##   "id":"low_temp",
    ##    "exec_time":0
    ##}
	def test_client(self,client):
		for device in client.devices:
			for zone in device.zones:
				if self.test_client_zone(client,device,zone):
				 	break;

		return {
			'id': self.id,
			'exec_time':self.exec_time
		}

class LowTempAlert(AbstractAlert):
	
	## result: true if alert executed or false if not
	def test_client_zone(self, client, device, zone):
	
		conf = self.conf;

		## CHECK CURRENT TEMPERATURE
		if zone.current_temp > conf['temp']:
			log_debug('LowTempAlert: test_client_zone: skip alert because alert temp='+str(conf['temp']))
			self.exec_time = 0
			return False
	
		
		## CHECK WHEN WE SEND THIS ALERT AT LAST TIME
		now = int(time.time())
		if 'exec_time' in self.data:
			last_time = self.data['exec_time']
			end_time = last_time + self.conf['period']
			if now < end_time:
				log_debug('LowTempAlert: test_client_zone: skip alert because need wait for additional '+str(end_time-now)+' secs')
				self.exec_time = last_time
				return False
		
		self.exec_time = now
		
		log_debug('LowTempAlert: test_client_zone: run alert because alert temp='+str(conf['temp'])+'  cond='+str(zone.current_temp > conf['temp']))
		## current temp is equal or lower than alert temperatur

		template =  Teplo500.Emailer.EmailTemplate('low_temp')
		template.client_name= client.name
		template.current_temp = temp_to_str(zone.current_temp)
		template.zone_name = zone.name

		emailer = Teplo500.Emailer.Emailer(client.alert_email)
		emailer.set_template(template)
		if not emailer.send():
			log_error('LowTempAlert: test_client_zone: can not send email')
		
		return True
	

def CreateAlert(id, alert_config, alert_data):

	if id == 'low_temp':
		return LowTempAlert(id, alert_config, alert_data)
	else:
		log_error('AlertFactory: CreateAlert: uknown alert id"'+alert_config['id']+'"')
		return None		

	
