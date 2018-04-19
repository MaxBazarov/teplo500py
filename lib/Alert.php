<?php

class AbstractAlert
{
	public $id='';
	public $conf=null; // object with client/config.conf/alerts/{} content
	public $data=null; // aarray with client/alerts.data content
	public $exec_time = 0;

	function __construct($id,$conf,$data) 
    {
    	$this->id = $id;
    	$this->conf = $conf;	
    	$this->data = $data;	
    }

	public function test_client_zone(SalusClient &$client, SalusDevice &$device, SalusZone &$zone){
		return false;
	}


	// result: 
	//{
    //   "id":"low_temp",
    //    "exec_time":0
    //}
	public function test_client(SalusClient &$client)
	{	
		foreach($client->devices as $device){
			foreach($device->zones as $zone){				
				if( $this->test_client_zone($client,$device,$zone) ) break;
			}						
		}	

		return array(
			'id'=>$this->id,
			'exec_time'=>$this->exec_time
		);
	}
	
}

class LowTempAlert extends AbstractAlert
{
	// result: true if alert executed or false if not
	public function test_client_zone(SalusClient &$client,SalusDevice &$device, SalusZone &$zone)
	{
		$conf = $this->conf;

		// CHECK CURRENT TEMPERATURE
		if( $zone->current_temp > $conf->temp ){					
			log_debug('LowTempAlert: test_client_zone: skip alert because alert temp='.$conf->temp);
			$this->exec_time = 0;
			return false;
		}
		
		// CHECK WHEN WE SEND THIS ALERT AT LAST TIME
		$now = time();
		if(array_key_exists('exec_time',$this->data)){		
			$now = time();
			$last_time = $this->data['exec_time'];
			$end_time = $last_time + $this->conf->period;
			if( $now < $end_time ){
				log_debug('LowTempAlert: test_client_zone: skip alert because need wait for additional '.($end_time-$now).' secs');
				$this->exec_time = $last_time;
				return false;
			}			
		}	
		$this->exec_time = $now;

		
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
