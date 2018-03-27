<?php

include 'AbstractApp.php';
include 'SalusConnect.php';

class CmdApp extends AbstractApp
{

	private $cmd='update_all';
	private $log_debug=false;

	function __construct(){
		parent::__construct();		
	}

	
	function cmd_print_args()
	{
		print 'Command line arguments: --cmd create|update_all --mode real|emul --emul online|offline  --debug --help';
	}

	// return true or false
	function parse_cmd_line()
	{

		$args = getopt('',array('cmd:','mode:','help','debug','emul:'));

		if( isset($args['help']) )
		{
			$this->cmd_print_args();
			exit;
		}

		$this->log_debug = isset($args['debug']);

		if( isset($args['cmd']) )
		{
			$cmd = $args['cmd'];
			switch ($cmd){
				case 'create':
				case 'update_all':
					break;
				default:
					// unknown cmd
					log_error('app_init: unknown "cmd"='.$cmd);
					$this->cmd_print_args();
					return false;
					break;
			} 
			$this->cmd = $cmd;
		}

		if( isset($args['mode']) )
		{
			switch ($args['mode']) {
				case 'real':				
					$this->salus->set_mode(SalusConnect::MODE_REAL);
					break;			
				case 'emul':				
					$this->salus->set_mode(SalusConnect::MODE_EMUL);
					break;				
				default:
					// unknown application mode
					log_error('app_init: unknown "mode"='.$args['mode']);
					$this->cmd_print_args();
					return false;
					break;
			}		
		}	

		if( isset($args['emul']) )
		{		
			switch ($args['emul']) {
				case 'online':				
					$this->salus->set_emul_submode( SalusConnect::EMUL_ONLINE );
					break;			
				case 'offline':				
					$this->salus->set_emul_submode( SalusConnect::EMUL_OFFLINE );
					break;				
				default:
					// unknown application mode
					log_error('app_init: unknown "emul"='.$args['emul']);
					$this->cmd_print_args();
					return false;
					break;
			}		
		}	


		return true;
	}


	function log_text($level=UTILS_LOG_OK,$text1,$text2='')
	{
		if($level == UTILS_LOG_DBG and !$this->log_debug) return true;

		$date = new DateTime("now",new DateTimeZone('Europe/Moscow'));
		$time = $date->format('Y-m-d H:i:s');
		print $time;

		switch($level){
			case UTILS_LOG_OK:
				print ' [OK ] ';break;
			case UTILS_LOG_ERR:
				print ' [ERR] ';break;
			case UTILS_LOG_DBG:
				print ' [DBG] ';
				break;
		}
		print $text1.$text2."\n";	
		return true;
	}

	function run_server()
	{		
		$iteration = 0;
		while(++$iteration<100)
		{
			log_ok('CmdApp: run: iteration #'.$iteration);
			$this->salus->create_load_clients();
			$this->salus->update_clients_from_site();

			log_ok('CmdApp: run: completed iteration #'.$iteration);
			sleep($this->config->defaults->auto_update);
		}

		
	}

	function run_once()
	{
		switch($this->cmd){
			case 'update_all':
				if(!$this->salus->create_load_clients()) return false;		
				if(!$this->salus->update_clients_from_site(true)) return false;	
				return;
			case 'create':
				$client = SalusClient::Factory_CreateAndRegister('Nikolay','89268884889@mail.ru','****');
				if(!$client){
					log_error('CmdApp: run: failed to create and register new client');					
				}else{
					log_ok('CmdApp: run: created and registered new client');
				}
				$client->update_from_site();
				$client->save_data();

				return;
			break;
		}

	}
}
?>
