import urllib.parse as urlparse
import cgi
import os.path


from web_utils import *
import AbstractApp
import AbstractPage
import AbstractREST
import WebLoginHelper
import SalusConnect

CONSTS = {
	'ORG_SITE' : 'https://teplo500.ru'
	'LOGIN_SUBURL' : '/index.php?page=login'
	'LOGOUT_SUBURL' : '/index.php?page=logout'
	'HOME_SUBURL' : '/index.php?page=home'
	'SETTINGS_SUBURL' : '/index.php?page=settings'
	'ACCOUNT_SUBURL' : '/index.php?page=account'
}
	

class WebApp(AbstractApp):


	def __init__(self):
		super().__init__(self)

		self.client = None
		self.login_helper = None
		self.rest_page = None

		self.client_id = ''
		self.page = ''

		self.url = '' ## TODO: initialise URL
		self.get_params = urlparse.parse_qs(urlparse.urlparse(self.url).query)
		self.form = cgi.FieldStorage()
	
	def init(self):
		if not super().init(self):
			return False

		## check files
		messages_path = self._messages_log_path()

		## create messages log file if it doesn't exist
		if not os.path.isfile(messages_path):
			try:
				with open(messages_path, 'w') as fp:
		
		
		## prepare login cookie management helper
		self.login_helper = WebLoginHelper.Create()
		if not self.login_helper:
			return log_error('WebApp: init(): can not create login helper')

		client_id = self.login_helper.try_login()
		if client_id!=''
   			self.client = SalusClient.CreateAndLoad(client_id)
   			if self.client:
   				$self->client_id = client_id
		
		## switch salus mode
		self.salus.set_mode(self.config['web']['salus_mode']=='real'?SalusConnect.MODE_REAL:SalusConnect.MODE_EMUL);		
			
		return True

	def get_client_id(self):
		return self.client_id

	def save_login(self,client_id):
   		if client_id=='':
   			return False
		self.client_id = client_id
   		self.client = SalusClient.CreateAndLoad(self.client_id);
   		self.login_helper.save_login(client_id)
   		return True
   	

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