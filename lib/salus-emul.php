<?php


define("EMUL_DEVICES_ONLINE_FILE",'/local/fakes/devices_online.html');
define("EMUL_DEVICES_OFFLINE_FILE",'/local/fakes/devices_offline.html');


// args:
// return: 
//   true=success or false=failed
function emul_load_devices()
{
	global $app;
	
	$file_name = $app->home_path().($app->salus->emul_submode()==SalusConnect::EMUL_ONLINE? EMUL_DEVICES_ONLINE_FILE: EMUL_DEVICES_OFFLINE_FILE);
	log_debug('emul_load_devices. file name='.$file_name);

	if (!file_exists($file_name)) {
		log_error('No '.$file_name.' file');
		return false;
	}

	$content = file_get_contents($file_name);
	if ($content === false) {
		log_error('Can not load '.$file_name);
		return false;
	}

	log_ok('Loaded '.$file_name);
	return $content;

}


?>