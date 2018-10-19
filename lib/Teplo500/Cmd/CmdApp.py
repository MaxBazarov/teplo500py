from Teplo500.core import *
from Teplo500.AbstractApp import * 
import Teplo500.SalusConnect

import argparse
import time
from datetime import datetime

class CmdApp(AbstractApp):

	def __init__(self):
		super().__init__()
		self.cmd = 'update_all'
		self.log_debug = False
		
	def init(self):
		if not super().init(): return False
		print("CmdApp.init()")
		print(self.salus)		

		return True


	def cmd_print_args(self):
		print('Command line arguments: --cmd create|update_all --mode real|emul --emul online|offline  --debug --help\n')
	
	def parse_cmd_line(self):
		parser = argparse.ArgumentParser(description='Controling teplo500.')
		parser.add_argument('--cmd',required=True)
		parser.add_argument('--mode',default='real')
		parser.add_argument('--emul',default='online')
		parser.add_argument('--debug')
		
		args = parser.parse_args()

		self.log_debug = args.debug is not None

		if args.cmd != 'create' and args.cmd != 'update_all':
			## unknown cmd
			log_error('app_init: unknown "cmd"='+args.cmd)
			self.cmd_print_args()
			return False			
		
		self.cmd = args.cmd;

		if args.mode == 'real' :				
			self.salus.set_mode(SalusConnect.MODE_REAL)
		elif args.mode == 'emul':				
			self.salus.set_mode(SalusConnect.MODE_EMUL)
		else:
			## unknown application mode
			log_error('app_init: unknown "mode"='+args.mode)
			self.cmd_print_args()
			return False	

		if args.emul == 'online':				
			self.salus.set_emul_submode( SalusConnect.EMUL_ONLINE )
		elif args.emul == 'offline':				
			self.salus.set_emul_submode( SalusConnect.EMUL_OFFLINE )
		else: ##unknown application mode
			log_error('app_init: unknown "emul"='+args.emul);
			self.cmd_print_args()
			return False

		return True

	def log_text(self, level, text1, text2=''):
		date = datetime.now()
		time = date.strftime('%y-%m-%d %H:%M:%S')	
		
		prefixes={
			Log.OK:' [OK ] ',
			Log.ERR:' [ERR ] ',
			Log.DBG:' [DBG ] '
		}
		print('['+time+']'+ prefixes[level] + text1 + text2)
		
		return True

	def run_server(self):
		iteration = 0

		while (++iteration<100):		
			log_ok('CmdApp: run: iteration #'+iteration)
			self.salus.create_load_clients()
			self.salus.update_clients_from_site()

			log_ok('CmdApp: run: completed iteration #'+iteration)
			time.sleep(self.config['defaults']['auto_update'])	
	

	def run_once(self):
		
		if(self.cmd=='update_all'):
			if( not self.salus.create_load_clients()): return False
			if( not self.salus.update_clients_from_site(True)): return False	
			return
		elif self.cmd == 'create':
			client = SalusClient.Factory_CreateAndRegister('Nikolay','89268884889@mail.ru','****')
			if(client is None):
				log_error('CmdApp: run: failed to create and register new client')
			else:
				log_ok('CmdApp: run: created and registered new client')
				
				client.update_from_site()
				client.save_data()
		