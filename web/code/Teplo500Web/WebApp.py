import urllib.parse as urlparse
import cgitb
import cgi
import os.path
import sys
import json
from datetime import date

from flask import make_response,request

from Teplo500Web.web_utils import *
from Teplo500.utils import *
from Teplo500.AbstractApp import *

import Teplo500.SalusConnect
from Teplo500.SalusClient import *

from Teplo500Web.REST.AbstractREST import *
from Teplo500Web.REST.ClientREST import *
from Teplo500Web.Pages.AbstractPage import *
import Teplo500Web.WebLoginHelper

from Teplo500Web.Pages.AccountPage import *
from Teplo500Web.Pages.HomePage import *
from Teplo500Web.Pages.LoginPage import *
from Teplo500Web.Pages.SettingsPage import *
from Teplo500Web.Pages.ZoneEdit import *


def CreateAndInit():
	wa = WebApp()
	if not wa.init():
		return None			
	return wa


class WebApp(AbstractApp):

	def __init__(self):
		super().__init__()

		self.client = None
		self.login_helper = None
		self.rest_page = None

		self.client_id = ''
		self.page = ''

		self.urls = {
			'ORG_SITE' : 'https://teplo500.ru',
			'LOGIN_SUBURL' : '/login',
			'LOGOUT_SUBURL' : '/logout',
			'HOME_SUBURL' : '/home',
			'SETTINGS_SUBURL' : '/settings',
			'ACCOUNT_SUBURL' : '/account'
		}		

		self.url = '' ## TODO: initialise URL
		self.get_params = urlparse.parse_qs(urlparse.urlparse(self.url).query)

		self.new_cookies = []
			
	
	def init(self):
		if not super().init(): return False

		page = request.full_path.replace("?","/").split("/")[1]
		self.page = page if page!="" else "home"

		## check files
		messages_path = self._messages_log_path()

		## create messages log file if it doesn't exist
		if not os.path.isfile(messages_path):
			fp = open(messages_path, 'w')
			fp.close()
						
		## prepare login cookie management helper
		self.login_helper = Teplo500Web.WebLoginHelper.Create()
		if not self.login_helper:
			return log_error('WebApp: init(): can not create login helper')

		client_id = self.login_helper.try_login()
		if client_id!='':
   			self.client = SalusClient_CreateAndLoad(client_id)
   			if self.client:
   				self.client_id = client_id
		
		## switch salus mode
		self.salus.set_mode(Teplo500.SalusConnect.MODE_REAL if self.config['web']['salus_mode']=='real' else Teplo500.SalusConnect.MODE_EMUL)
			
		return True

	def set_cookie(self,key,value,max_age):
		self.new_cookies.append({
			'key':key,
			'value':value,
			'max_age':max_age
		})


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

	def redirect_local(self,suburl):
		return self.redirect(self.base_url()+suburl)

	def redirect_to_login(self):
		self.save_logout()

		login_url = self.base_url() + self.urls['LOGIN_SUBURL']
		return self.redirect(login_url)
		

	def _messages_log_path(self):	
		return self.home_path()+'/local/logs/messages.log'
	
	
	def log_text(self, level, text1, text2=''):
		date = datetime.now()
		time = date.strftime('%y-%m-%d %H:%M:%S')	

		prefixes={
			Log.OK:' [OK ] ',
			Log.ERR:' [ERR ] ',
			Log.DBG:' [DBG ] '
		}

		fp = open(self._messages_log_path(), 'a')
		fp.write('['+time+']'+ prefixes[level] + text1 + text2 +"\n")
		fp.close()

		return True


	def run_rest(self):
		rest_obj = None

		if self.client_id=='':
			return AbstractREST.show_non_auth_error()
		
		if self.rest_page == 'client':			
			rest_obj =  ClientREST()
		else:
			return AbstractREST.ShowUknownCmd()
		
		return rest_obj.run()

	def create_response(self,content):
		response = make_response(content)
		for cookie in self.new_cookies:			
			response.set_cookie(cookie['key'], cookie['value'],cookie['max_age'])
		return response

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
		
		## init current page		)
		if self.page=='login':
			page_obj = LoginPage.LoginPage()
		elif self.page=='account':
			page_obj = AccountPage.AccountPage()
		elif self.page=='settings':
			page_obj = SettingsPage.SettingsPage()
		elif self.page=='logout':
			return self.redirect_to_login()
		else:
			log_debug('home')
			page_obj = HomePage()

		return self.create_response(page_obj.run())
