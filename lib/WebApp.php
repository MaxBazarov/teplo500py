<?php

include 'web_utils.php';
include 'AbstractApp.php';
include 'AbstractPage.php';
include 'AbstractREST.php';
include 'WebLoginHelper.php';
include 'SalusConnect.php';

class WebApp extends AbstractApp
{
	const ORG_SITE = 'https://teplo500.ru';

	const LOGIN_SUBURL = '/index.php?page=login';
	const LOGOUT_SUBURL = '/index.php?page=logout';
	const HOME_SUBURL = '/index.php?page=home';
	const SETTINGS_SUBURL = '/index.php?page=settings';
	const ACCOUNT_SUBURL = '/index.php?page=account';

	public $client = null;
	public $login_helper = null;
	public $rest_page = null;

	private $client_id = '';  
	private $page = '';	

	function __construct(){
		parent::__construct();
		//session_start();		
	}

	function init(){
		if( !parent::init() )  return false;

		// check files
		$messages_path = $this->_messages_log_path();
		if(!file_exists($messages_path)){
			$file = fopen($messages_path,'x');	
			if(!$file){
				return log_error('Webapp: init: can not create '.$messages_path);
			}
			fclose($file);
		}

		// prepare login cookie management helper
		$this->login_helper = WebLoginHelper::Factory_Create();	
		if(!$this->login_helper) return log_error('WebApp: init(): can not create login helper');
		$client_id = $this->login_helper->try_login();
		if($client_id!==false){			
   			$this->client = SalusClient::Factory_CreateAndLoad($client_id);
   			if($this->client) $this->client_id = $client_id;
		}

		// switch salus mode
		$this->salus->set_mode($this->config->web->salus_mode=='real'?SalusConnect::MODE_REAL:SalusConnect::MODE_EMUL);		
			
		return true;
	}


	function get_client_id(){
		return $this->client_id;
	}

	function __destruct() {
       parent::__destruct();       
       //session_commit();
   }


   function save_login($client_id){    		
   		if($client_id==='') return false;
		$this->client_id = $client_id;
   		$this->client = SalusClient::Factory_CreateAndLoad($this->client_id);
   		$this->login_helper->save_login($client_id);   		
   		return true;
   	}

   	function save_logout(){    		
   		$this->login_helper->logout();   		
   		$this->client = null;
   		$this->client_id = '';   
   		
   		return true;
   	}

   

	function web_path()
	{
		return $this->home_path().'/web';
	}

	function page()
	{
		return $this->page;
	}

	function base_url()
	{
		return $this->config->web->base_url;
	}

	function redirect($url)
	{
		header('Location: '.$url);
		exit;
	}

	function redirect_local($suburl)
	{		
		return $this->redirect($this->base_url().$suburl);
	}

	function redirect_to_login()
	{
		$this->save_logout();

		$login_url = $this->base_url().$this::LOGIN_SUBURL;
		return $this->redirect($login_url);
	}	


	private function _messages_log_path()
	{
		return $this->home_path().'/local/logs/messages.log';		
	}
	

	function log_text($level,$text1,$text2='')
	{
		$date = new DateTime("now",new DateTimeZone('Europe/Moscow'));
		$time = $date->format('Y-m-d H:i:s');

		$level_text = '';
		switch($level){
			case UTILS_LOG_OK:
				$level_text=' [OK ] ';break;
			case UTILS_LOG_ERR:
				$level_text= ' [ERR] ';break;
			case UTILS_LOG_DBG:
				$level_text= ' [DBG] ';
				break;
		}


		$file = fopen($this->_messages_log_path(),'a');	
		fwrite($file,'['.$time.']'.$level_text.$text1.$text2."\n");		
		fclose($file);
		return true;
	}

	function run_rest()
	{
		$rest_obj = null;

		if($this->client_id=='') return AbstractREST::show_non_auth_error();
		
		switch ($this->rest_page){
			case 'client':
				include_once '../web/rest/ClientREST.php';
				$rest_obj =  new ClientREST();
				break;		
			default:
				return AbstractREST::ShowUknownCmd();
				break;
		}
		return $rest_obj->run();
	}		



	function run()
	{
		$this->rest_page = http_get_param("rest_page");
		if($this->rest_page!='') return $this->run_rest();

		$this->page = http_get_param("page");
		$page = null;

		// pre-checks
		if($this->page=='') $this->page = 'home';	
		if($this->client_id=='') $this->page = 'login';		
		

		switch ($this->page){
			case 'login':
				include_once '../web/Pages/LoginPage.php';
				$page = new LoginPage();
				break;
			case 'account':
				include_once '../web/Pages/AccountPage.php';
				$page = new AccountPage();
				break;
			case 'settings':
				include_once '../web/Pages/SettingsPage.php';
				$page = new SettingsPage();
				break;
			case 'logout':
				return $this->redirect_to_login();
			case 'home':
			default:
				include_once '../web/Pages/HomePage.php';
				$page = new HomePage(); 			
				break;
		}

		$page->run();


		return true;
	}

}
?>