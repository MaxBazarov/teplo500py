from utils.py import *
import os, time, sys
import SalusConnect

class AbstractApp:	

	def __init__(self):
    	self.salus = SalusConnect()
    	self.timezone = '' ## example: Europe/Moscow
		self.lang = '' ## example: en
		self.config = {}  ## dictionary with system.conf content
		self.salus = None ## ref to SalusConnect instance

		self.locales = {}
	
    def __del__(self):
    	pass
	
    def init(self):
		
		## load system config
		config = load_json_config('../local/system.conf')
		if config is None:
		   return False		   
		self.config = config

		self.lang = config['defaults']['lang']
		self.timezone = config['defaults']['timezone'];

		os.environ['TZ'] = self.timezone
		time.tzset()
		 
		return True
	

	def log_text(self, level = Log.OK, text1, text2=None):	
		## should be re-impplented in child class
		return sys.exit()

	def home_path(self):
		return self.config['home_path']
	
	def clients_folder(self):
		return self.home_path()+'/local/clients';
	

	def translate_string(self,str):
		lang = self.lang;
		if lang == 'en':
			return str

		## load new locale
		if lang not in self.locales:

			new_locale = load_json_config('../system/locales/strings.'+lang)
			if new_locale is None:
				log_error('AbstractApp: translate_string: No locale for lang"'+lang+'"')
				return 'NO LOCALE FOR '+lang
			
			self.locales[lang] = new_locale
		

		## find string
		if str in self.locales[lang]:			
			return self.locales[lang][str]
		else:
			## check context in key id
			if str.find('/')==-1:
				return str				
			else:
				return str.split('/')[0]
		

