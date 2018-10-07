from datetime import date
import time
import os.path

from flask import request

from Teplo500.utils import *

## return WebLoginHelper instance or false(error) 
def Create():
	helper = WebLoginHelper()
	if not helper.init():
		return log_error('WebLoginHelper::Factory_Create() can not init helper')
	return helper

class WebLoginHelper:

	def __init__(self):
		self.login_id = ''

	def init(self):
		return True

	def set_first_cookie(self):
		if self.login_id!='':
			return True
		self.set_cookie()
	
	def set_cookie(self,login_id=None):  		
		if login_id is None:
			self.login_id = uniqid()
		else:
			self.login_id = login_id
			
		app = get_app()
		app.set_cookie('login_id',self.login_id,int(time.time())+60*60*24*360)
		return True


	def _get_folder_path(self):
		log_error('----------------------')
		app = get_app()
		return app.home_path()+'/local/logins'


	def logout(self):
		if self.login_id=='':
			return True

		if not self._delete_login_file():
			return log_error('WebLoginHelper.logout() can not delete login file')		
		 
		return self.set_cookie('')

	## return client_id or false
	def try_login(self):	
		log_d = lambda message: log_debug('WebLoginHelper: try_login(): '+message)

		log_d('staring... ')

		## check filled cookie existing 
		login_id_cookie = request.cookies.get('login_id')
		if login_id_cookie != '':
			self.login_id = clear_textid(login_id_cookie)
		
		log_d('login_id='+self.login_id)
		if self.login_id=='':
			return False;

		## check login file existing
		file_path = self._path_to_login(self.login_id)
		if not os.path.exists(file_path):
			return True

		## load login file
		login = load_json_config(file_path)
		if login is None:
			log_d('can not load config '+file_path)
			return False		
		
		client_id = login['client_id']
		
		log_d('restored client_id='+client_id )
		return client_id	


	def save_login(self,client_id):
		log_d = lambda message: log_debug('WebLoginHelper: save_login(): '+message)

		## delete old login
		if not self._delete_login_file():
			 return log_error('WebLoginHelper.try_login() failed to delete old file')

		log_d('deleted old login_id='+self.login_id )
		self.login_id = ''

		## generate new login_id
		self.login_id = uniqid()
		login = {
			'client_id':client_id,
			'last_client_ip': request.remote_addr,
			'last_time':date_now_txt
		}
		log_d('generated new login_id='+self.login_id)

		## save new login data to file
		file_path = self._path_to_login(self.login_id)
		if not save_json_config(file_path,login):
			return log_error('WebLoginHelper: generate_login: failed to save in "'+file_path+'"')	
	
		log_d('saved new login to file='+file_path)

		## send new login id to client
		self.set_cookie(self.login_id)
	
		return True


	def _path_to_login(self,login_id):
		return self._get_folder_path()+'/'+login_id+'.data'
	

	def _delete_login_file(self):
		if self.login_id=='': return True

		## prepare to delete existing login
		file_path = self._path_to_login(self.login_id)		
		if os.path.exists(file_path):
			os.remove(file_path)
		
		return True   	