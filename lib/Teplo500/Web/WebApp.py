import urllib.parse as urlparse
import cgitb
import cgi
import os.path
import sys
from datetime import date


from web_utils import *
from utils import *
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
		

		cgitb.enable()
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
   			self.client = SalusClient_CreateAndLoad(client_id)
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
   		self.client = SalusClient_CreateAndLoad(self.client_id);
   		self.login_helper.save_login(client_id)
   		return True

   	def save_logout(self):
   		self.login_helper.logout()
   		self.client = None
   		self.client_id = '';      		
   		return True
  
  	def web_path(self):
		return self.home_path()+'/web'
	

	def page(self):
		return self.page
	
	def base_url(self):
		return self.config['web']['base_url']
	
	def redirect(self,url):
		print("Location: "+url+"\n")
		sys.exit()

	def redirect_local($suburl)
		return self.redirect(self.base_url().$suburl);

	def redirect_to_login(self):
		self.save_logout()

		login_url = self.base_url() + CONSTS['LOGIN_SUBURL'];
		return self.redirect(login_url)
		

	def _messages_log_path(self):	
		return self.home_path()+'/local/logs/messages.log'
	
	
	def log_text(self, level, text1, text2=''):
		date = datetime.now()
		time = date.strftime('%y-%m-%d %H:%M:%S')	

		prifixes={
			Log.OK:' [OK ] ',
			Log.ERR:' [ERR ] ',
			Log.DBG:' [DBG ] '
		}

		try:
			with open(self._messages_log_path(), 'a') as fp:					
				fp.write('['+time+']'+ prefixes[level] + text1 + text2 +"\n")

		return True


	def run_rest(self):
		rest_obj = None

		if self.client_id='':
			return AbstractREST.show_non_auth_error()
		
		if self.rest_page = 'client':
			import('../web/rest/ClientREST')
			rest_obj =  ClientREST().ClientREST()
		else:
			return AbstractREST.ShowUknownCmd()
		
		return rest_obj.run()


	def run(self):
	
		self.rest_page = http_get_param("rest_page")
		if self.rest_page!='':
			return self.run_rest()

		self.page = http_get_param("page")
		page_obj = None

		## pre-checks
		if self.page=='':
			self.page = 'home'
		if self.client_id=='':
			self.page = 'login'
		
		## init current page
		if self.page=='login':
			import('../web/Pages/LoginPage')
			page_obj = LoginPage.LoginPage()
		elif self.page=='account':
			import('../web/Pages/AccountPage')
			page_obj = AccountPage.AccountPage()
		elif self.page=='settings':
			import('../web/Pages/SettingsPage')
			page_obj = SettingsPage.SettingsPage()
		elif self.page=='logout':
			return self.redirect_to_login()
		else:
			import('../web/Pages/HomePage')
			page_obj = HomePage.HomePage()

		page_obj.run()

		return True
	