<?php


include '../lib/CmdApp.php';

$app = new CmdApp;
if(!$app->init()){
	log_error('Can not initiate app');
	exit -1;
}

if( !$app->parse_cmd_line() ) exit -1;
$app->run_once();

?>
