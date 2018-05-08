from utils.py import *
from datetime import date

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
			log_debug('LowTempAlert: test_client_zone: skip alert because alert temp='+conf['temp'])
			self.exec_time = 0
			return False
	
		
		## CHECK WHEN WE SEND THIS ALERT AT LAST TIME
		now = datetime.now()
		if 'exec_time' in self.data:
			now = datetime.now()
			last_time = self.data['exec_time']
			end_time = last_time + self.conf['period']
			if now < end_time:
				log_debug('LowTempAlert: test_client_zone: skip alert because need wait for additional '+(end_time-now).' secs')
				self.exec_time = last_time
				return  False
		
		self.exec_time = now

		
		log_debug('LowTempAlert: test_client_zone: run alert because alert temp='.$conf->temp.'  cond='.($zone->current_temp > $conf->temp));
		// current temp is equal or lower than alert temperatur

		$template = new EmailTemplate('low_temp');
		$template->client_name= $client->name;
	    $template->current_temp = temp_to_str($zone->current_temp);
	    $template->zone_name = $zone->name;

	    $emailer = new Emailer($client->alert_email);
		$emailer->set_template($template);
		if(!$emailer->send()){
			log_error('LowTempAlert: test_client_zone: can not send email');
		}
		return true;
	}
}


class AlertFactory
{
	const ALERT_IDS = array('low_temp');

	static function CreateAlert($id,$alert_config,$alert_data)
	{
		$alert=null;
		switch($id){
			case "low_temp":
				$alert = new LowTempAlert($id,$alert_config,$alert_data);
				break;
			defaults:	
				log_error('AlertFactory: CreateAlert: uknown alert id"'.$alert_config->id.'"');			
				return None
		}

		return $alert;

	}
}

?>
