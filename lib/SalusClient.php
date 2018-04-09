<?php

include "Emailer.php";
include "Alert.php";
import SalusHistoryHelper

class SalusClient
{
	
	public $id = '';
	public $name = '';

	public $alert_email = '';
	public $devices = array(); // list of {SalusDevice}

	public $data_updated_time = 0; // time of last data update

	// user creds
	private $login_email = '';
	private $login_password = '';		
	public $config = array();
	

	private $PHPSESSID = '';


	// args:
	//	client_id : email address
	// result
	//  ref to SalusClient or false

	static function Factory_CreateAndLoad($client_id)
	{
		log_debug('Factory_CreateAndLoad: creating client '.$client_id.'...');

		$client_id = ltrim(rtrim($client_id));
		if($client_id===''){
			return log_error('Factory_CreateAndLoad: construct: ID undefined');	
		}

		$client = new SalusClient($client_id);
		
		if($client->load()==false){
			return log_error('Factory_CreateAndLoad: run: can not load client');
		}

		log_debug('Factory_CreateAndLoad: created client '.$client_id);

		return $client;
	}

	// args:
	//	email : email address
	//	pswd : password
	// result
	//  ref to SalusClient or false

	static function Factory_CreateAndRegister($name,$email,$password)
	{
		log_debug('Factory_CreateAndRegister: creating client');

		$client = new SalusClient($email);	
		if(!$client->_set_name($name)) return false;
		if(!$client->_set_login($email,$password)) return false;

		if(!$client->register()){
			return log_error('Factory_CreateAndRegister: run: can not register new client');
		}

		if(!$client->load()){
			return log_error('Factory_CreateAndRegister: run: can not load client');
		}

		log_debug('Factory_CreateAndRegister: created client '.$client_id);

		return $client;
	}


	function __construct($id) 
    {
    	$if = htmlspecialchars(ltrim(rtrim($id)));
    	$this->id = $id;     	
    }


	// check do we need to update it right now or not?
    function is_updated_required(){
    	if($this->data_updated_time==0) return true;

		$conf_period = $this->get_auto_update();
		if($conf_period===0) return true;

		$now_period = time() - $this->data_updated_time;
		return $now_period >= $conf_period;

    }

	function update_from_site(){
		log_ok('[CLIENT '.$this->id.'] Updating from site...');		

		if($this->_update_device_list_from_site()==false){
			return log_error('SalusClient: run: can not init devices');
		}

		if($this->_load_devices_from_site()==false){
			return log_error('SalusClient: run: can not load devices');
		}
		return true;
	}

	function switch_esm($enable_esm){
		$log_d = function($message){ return log_debug('[CLIENT '.$this->id.'] switch_esm(): '.$message);};
		$log_e = function($message){ return log_error('[CLIENT '.$this->id.'] switch_esm(): '.$message);};
		$log_ok = function($message){ return log_ok('[CLIENT '.$this->id.'] switch_esm(): '.$message);};


		$log_d('switching into '.$enable_esm);

		$success = true;
		array_map(
			function($device){
				if(!$device->switch_esm($enable_esm)) $success = false;
			}
			,$this->devices
		);		
		if(!$success) return $log_e('failed to switch');

		$log_ok('switched ESM successfully');

		if(!$this->update_from_site()) return $log_e('failed to update data');
        if(!$this->save_updated()) return $log_e('failed to save updated data');

		return true;
	}


	function get_phpsessionid()
	{		
		return $this->PHPSESSID;
	}

	function get_auto_update(){
		global $app;
		return property_exists($this->config,'auto_update')?
			$this->config->auto_update
			:$app->config->defaults->auto_update
		;
	}

	function get_auto_update_txt(){
		$period = $this->get_auto_update();
		if($period==0) return locstr('Off');

		if($period<3600) return ($period / 60).' '.locstr('minute(s)/timediff');
		if($period<86400) return ($period / 3600).' '.locstr('hour(s)/timediff');
		return ($period / 86400).' '.locstr('day(s)/timediff');
	}

	function validate_password($pswd){
		return $pswd == $this->login_password;
	}

	function run_alerts()
	{
		// load old aler data
		$data = $this->_load_json_config('alerts.data',true,true);
		if($data===false){
			$data = array(
				'alerts'=>array()
			);
		}

		// iterate know alerts
		$new_data = array(
			'alerts'=>array()
		);
		foreach(AlertFactory::ALERT_IDS as $id){
			$conf = $this->config->alerts->{$id};
			if(!$conf or !$conf->on) continue;

			log_debug('SalusClient: run_alerts: test alert'.$id);

			$alert = AlertFactory::CreateAlert($id,$conf,$data['alerts'][$id]);
			if(!$alert){
				return log_error('SalusClient: _run_zone_alert: can create Alert instance');	
			}
			$new_data['alerts'][$id] = $alert->test_client($this);
		}

		// save new data
		{
			if(!$this->_save_json_config('alerts.data',$new_data))
			{
				log_eror('SalusClient: run_alerts: can not save new data');
				return false;
			}	
		}

		return true;
	}

	// Load client, devices and zones date stored locally
	public function load()
	{		
		// READ AUTH CONFIG
		$auth_config = $this->_load_json_config('auth.conf');
		if($auth_config===false){
			log_error('SalusClient: load: can not load auth config');
			return false;
		}
		$this->login_email = $auth_config->email;
		$this->login_password = $auth_config->key;
		

		// READ MAIN CONFIG
		$config = $this->_load_json_config('client.conf');
		if($config===false){
			log_error('SalusClient: load: can not load config');
			return false;
		}
		$this->config = $config;
		$this->alert_email = $config->client->alert_email;
		$this->name = $config->client->name;



		// read existing data
		$this->devices = array();
		$data = $this->_load_json_config('client.data',false,true);
		if($data){
			$this->data_updated_time = $data->time;
			foreach($data->devices as $device_data){
				$device = new SalusDevice($this); 
				$device->load($device_data);
				array_push($this->devices,$device);
			}
		}
		log_debug('SalusClient: load: completed');
		return true;
	}


	function register()
	{
		global $app;

		// check client older for existing
		$path = $this->get_folder_path();
		if(!file_exists($path)){
			if(!mkdir($path)){
				log_error('SalusClient: register: can not create client folder "'.$path.'"');
				return false;
			}
			$history_path = $path.'/history';
			if(!mkdir($history_path)){
				log_error('SalusClient: register: can not create client history folder "'.$history_path.'"');
				return false;
			}
		}		

		// init default config
		$this->config = array(
			'client'=>array(
				'name'=>$this->name,
				'alert_email'=>$this->login_email
			),
			'alerts'=>$app->config->default_alerts			
		);


		$this->save_config();
		$this->save_auth();
		$this->save_data();

		return true;
	}

	function save_updated(){
//		if(!$this->save_history()) return false;
//		if(!$this->run_alerts()) return false;
		if(!$this->save_data()) return false;

		return true;
	}

	function save_auth()
	{
		$data = array(
			'email'=>$this->login_email,
			'key'=>$this->login_password
		);	

		if(!$this->_save_json_config('auth.conf',$data)) return log_error('SalusClient: save_auth: can not save client auth');
		return true;
	}

	function save_config()
	{

		if(!$this->_save_json_config('client.conf',$this->config)) return log_error('SalusClient: save_config: failed');
		return true;
	}


	function save_data()
	{	
		$data = $this->get_data_for_save();
		if(!$this->_save_json_config('client.data',$data)) return log_eror('SalusClient: save: can not save client data');
		$this->data_updated_time = $data['time'];
				
		return true;
	}


	function get_data_for_save()
	{
		return array(
			'time'=>time(),
			'date'=>date("Y M d H:i:s"),
			'devices'=>array_map(
				function($device){
					return $device->get_data_for_save();
				}
				,$this->devices
			)
		);
	}

	def save_history(self):
		return SalusHistoryHelper.save_client_history(self)
	


	function get_folder_path()
	{
		global $app;
		return $app->clients_folder().'/'.$this->id;
	}

	function get_device_by_id($id){
		foreach($this->devices as $dev){
			if($dev->id===$id) return $dev;
		}
		return false;
	}

	function get_zone_by_id($id){
		foreach($this->devices as $dev)
			foreach($dev->zones as $zone) if($zone->id==$id) return $zone;
		
		return false;
	}


	//////////////////////////////////////////////////////////// PRIVATE FUNCTIONS //////////////////////////////////////

	
	private function _set_login($email,$password)
	{
		// cleanup arguments
		$email = htmlspecialchars(ltrim(rtrim($email)));
		$password = htmlspecialchars(ltrim(rtrim($password)));

		if(!filter_var($email, FILTER_VALIDATE_EMAIL)) return false;
		if(strlen($password)==0) return false;

		// store
		$this->login_email = $email;
		$this->login_password = $password;

		return true;
	}

	private function _set_name($name)
	{
		// cleanup arguments
		$name = ltrim(rtrim($name));
		
		if(strlen($name)==0) return false;

		// store
		$this->name = $name;
		
		return true;
	}


	///////////////////////////////////////////// SAVE/LOAD CONFIGS ///////////////////////////////////////////////////////

	

 	private function _load_json_config($file_name,$assoc=false,$ignore_missing=false)
	{
		$path = $this->get_folder_path().'/'.$file_name;
		if(!file_exists($path)){
			if($ignore_missing)
				return $assoc?array():new stdClass();
			else
				return log_error('SalusClient: _load_json_config: can not find file "'.$path.'"');
		}
		return load_json_config($path,$assoc);
	}

	private function _save_json_config($file_name,$config)
	{
		$path = $this->get_folder_path().'/'.$file_name;
		$content = json_encode($config,JSON_PRETTY_PRINT);

		if($content===false){
			log_error('SalusClient: _save_json_config: can not encode config "'.$file_name.'" Error: '.json_last_error_msg());
			return false;
		}		

		if(!file_put_contents($path,$content)){
			log_error('SalusClient: _save_json_config: can not save config "'.$path.'"');
			return false;
		}		
		return true;

	}


	///////////////////////////////////////////// COMMUNICATION WITH SITE ///////////////////////////////////////////////////////


	// result: 
	//		true or false
	function login_to_site()
	{
		global $app;

		if( !$app->salus->is_real_mode() ){
			return true;
		}

		// GET FIRST COOKIE
		$data = array (
			'lang'=>'en'
		);
		req = net_http_request( SalusConnect::START_URL,SalusConnect::START_URL, $data,'GET', $this->PHPSESSID );	

		{
			$this->PHPSESSID = strval(req.cookies['PHPSESSID']);
			log_debug('login_to_site: PHPSESSID="'.$this->PHPSESSID.'"');
		}

		// TRY LOGIN
		{
			/* SETUP CONTEXT */
			$data = array (
				'IDemail' => $this->login_email,
				'password' => $this->login_password,
				'lang'=>'en',
				'login' => 'Login'
			);


			$result = net_http_request( SalusConnect::LOGIN_URL,SalusConnect::LOGIN_URL, $data,'POST', $this->PHPSESSID);
			if($result===false){
				return log_error('SalusClient: login_to_site: failed to get "'.SalusConnect::LOGIN_URL.'"');
			}

			return $result;
		}

	}


	// result: 
	//		true or false
	private function _update_device_list_from_site()
	{
		global $app;
		log_debug('SalusClient: _update_devices_from_site : started');

		$result = $this->login_to_site();
		if($result===false){
			log_error('SalusClient: _update_devices_from_site : failed  - can not ping');
			return false;
		}

		$devices_html = '';

		if($app->salus->is_real_mode()){
			// STORE DEVICES CONTENT
			log_debug('SalusClient: _update_devices_from_site : loaded real data from site');
			
			$devices_html = $result['content'];
			file_put_contents($app->home_path().'/local/output/devices.html',$devices_html);
		}elseif($app->salus->is_emul_mode()){
			log_debug('SalusClient: _update_devices_from_site : load faked data from local file');

			$devices_html = emul_load_devices();
		}else{
			return log_error('salus_login: unknown app mode='.$app->salus->mode());
		}	

		$this->_parse_html_devices($devices_html);	

		return true;
	}



	// args
	//		devices_html: string
	// return: true=success or false=failed
	private function _parse_html_devices(&$devices_html)
	{
		$log_d = function($message){
			log_debug('SalusClient: _parse_html_devices(): '.$message);
		};

		$log_d('starting...');
		$dom = new DOMDocument;
		libxml_use_internal_errors(true);
		if(!$dom->loadHTML($devices_html,LIBXML_NOWARNING)) return log_error('salus_parse_devices(): Can not parse devices from HTML');
		
		libxml_clear_errors();


		$xpath = new DOMXpath($dom);

		// search for <input name="devId" type="hidden" value="70181"/>
		$inputs_nodes = $xpath->query("//input[@name='devId']");

		if (is_null($inputs_nodes)) return log_error('salus_parse_devices: Can not find device definition in HTML');


		// ADD FOUND DEVICES
		foreach ($inputs_nodes as $input_node)
		{
			// GET ID	
			$id = get_node_attr_value($input_node,'value');		
			$log_d('id='.$id);		
			if($id === false) return log_error('salus_parse_devices: Can not ID atrribute in node definition');

			// TRY TO FIND ALREADY EXISTING DEVICE
			$existing_dev = $this->get_device_by_id($id);
			$dev = $existing_dev;

			if(!$dev){
				$dev = new SalusDevice($this,$id);
			}

			if(!$dev->init_from_dom($xpath,$input_node)) return log_error('salus_parse_devices: can not load device');

			// STORE NEW DEVICE
			if(!$existing_dev) array_push($this->devices,$dev);
		}
		
		$log_d('done');		
	}

	private function _load_devices_from_site()
	{
		foreach($this->devices as $dev) {
			if(!$dev->load_from_site()){
				log_error('SalusClient: load_devices: can not load device #'.$dev->id);
				return false;
			}			
		}

		return true;
	}

}

?>