import * from utils
import * from AbstractApp
import SalusConnect
import argparse
import time

from datetime import date

class CmdApp(AbstractApp):

	private $cmd='update_all';
	private $log_debug=false;

	def __init__(self):
		super().__init__(self)
		self.cmd = 'update_all'
		self.log_debug = False

	def cmd_print_args(self):
		print('Command line arguments: --cmd create|update_all --mode real|emul --emul online|offline  --debug --help\n')
	
	def parse_cmd_line(self):
		parser = argparse.ArgumentParser(description='Controling teplo500.')
		parser.add_argument('--cmd',required=True)
		parser.add_argument('--mode',default='real')
		parser.add_argument('--emul',default='online')
		parser.add_argument('--debug')
		parser.add_argument('--help')

		args = parser.parse_args()

		if args.help is not None:		{
			self.cmd_print_args();
			exit;

		self.log_debug = args.debug is not None

		if args.cmd != 'create' and args.cmd != 'update_all':
			## unknown cmd
			log_error('app_init: unknown "cmd"='+args.cmd)
			self.cmd_print_args()
			return False			
		}
		self.cmd = $cmd;

		if args.mode == 'real':				
			self.salus.set_mode(SalusConnect.MODE_REAL)
		else if args.mode == 'emul':				
			self.salus.set_mode(SalusConnect.MODE_EMUL)
		else ## unknown application mode
			log_error('app_init: unknown "mode"='+args.mode)
			self.cmd_print_args()
			return False	

		if args.emul == 'online':				
			self.salus.set_emul_submode( SalusConnect.EMUL_ONLINE )
		else if args.emul == 'offline':				
			self.salus.set_emul_submode( SalusConnect::EMUL_OFFLINE )
		else ##unknown application mode
			log_error('app_init: unknown "emul"='+args.emul);
			self.cmd_print_args()
			return False

		return True

	def log_text(self, level, text1, text2=''):
		date = datetime.now()
		time = date.strftime('%y-%m-%d %H:%M:%S')	

		prifixes={
			Log.OK:' [OK ] ',
			Log.ERR:' [ERR ] ',
			Log.DBG:' [DBG ] '
		}

		print('['+time+']'+ prefixes[level] + text1 + text2 +"\n")
		
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
			if(!self.salus.create_load_clients()) return False
			if(!self.salus.update_clients_from_site(true)) return False	
			return
		else if self.cmd == 'create':
			client = SalusClient.Factory_CreateAndRegister('Nikolay','89268884889@mail.ru','****')
			if(client is None):
				log_error('CmdApp: run: failed to create and register new client')
			else:
				log_ok('CmdApp: run: created and registered new client')
				
				client.update_from_site()
				client.save_data()
		