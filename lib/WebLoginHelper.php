<?php


class WebLoginHelper
{
	private $login_id = '';

	// return WebLoginHelper instance or false(error) 
	static function Factory_Create(){
		$helper = new WebLoginHelper();
		if(!$helper->init()){
			return log_error('WebLoginHelper::Factory_Create() can not init helper');
		}
		return $helper;
	}

	function __construct(){
	}

	function init(){
		return true;
	}

	function __destruct() {
   	}


   	function set_first_cookie(){
   		if($this->login_id!='') return true;
   		$this->set_cookie();
   	}
 
   	function set_cookie($login_id=false){   		
   		$this->login_id = $login_id===false?uniqid():$login_id;
   		setcookie('login_id',$this->login_id,time()+60*60*24*360);

   		return true;
   	}

   
   	private function _get_folder_path(){
   		global $app;
		return $app->home_path().'/local/logins';		
   	}

	function logout()
	{
		global $app;
		if($this->login_id=='')	return true;

		if(!$this->_delete_login_file()){
			return log_error('WebLoginHelper.logout() can not delete login file');
		}
		 
		return $this->set_cookie(''); 
	}

	// return client_id or false
	function try_login()
	{
		$log_d = function($message){
			log_debug('WebLoginHelper: try_login(): '.$message);
		};

		$log_d('staring... ');

		// check filled cookie existing 
		if(array_key_exists('login_id',$_COOKIE)){
			$this->login_id = clear_textid($_COOKIE['login_id']);		
		}
		$log_d('login_id='.$this->login_id);
		if($this->login_id=='') return false;

		// check login file existing
		$file_path = $this->_path_to_login($this->login_id);
		if(!file_exists($file_path)) return false;

		// load login file
		$login = load_json_config($file_path,true);
		if(!$login){
			$log_d('can not load config '.$file_path);
			return false;
		}
		$client_id = $login['client_id'];
		
		$log_d('restored client_id='.$client_id );
		return $client_id;
	}


   	function save_login($client_id)
   	{
   		$log_d = function($message){
			log_debug('WebLoginHelper: save_login(): '.$message);
		};

   		//delete old login   		
   		if(!$this->_delete_login_file()) return log_error('WebLoginHelper.try_login() failed to delete old file');
   		$log_d('deleted old login_id='.$this->login_id );
   		$this->login_id = '';

   		// generate new login_id
   		$this->login_id = uniqid();
   		$login = array(
   			'client_id'=>$client_id,
   			'last_client_ip'=>$_SERVER['REMOTE_ADDR'],
   			'last_time'=>time()
   		);
   		$log_d('generated new login_id='.$this->login_id);

   		// save new login data to file
   		$file_path = $this->_path_to_login($this->login_id);
   		if(!save_json_config($file_path,$login)){
   			return log_error('WebLoginHelper: generate_login: failed to save in "'.$file_path.'"');
   		}
   		$log_d('saved new login to file='.$file_path);

   		// send new login id to client
  		$this->set_cookie($this->login_id);
	
   		return true;
   	}

   	private function _path_to_login($login_id){
   		return $this->_get_folder_path().'/'.$login_id.'.data';
   	}

   	private function _delete_login_file(){
   		if($this->login_id==='') return true;

   		// prepare to delete existing login
		$file_path = $this->_path_to_login($this->login_id);		
		if(file_exists($file_path)){
			if(!unlink($file_path)) return log_error('WebLoginHelper._delete_login_file() can not delete login file"'.$file_path.'"');
		}
		return true;
   	}

}
?>
