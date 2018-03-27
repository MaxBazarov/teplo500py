<?php

include '../lib/WebApp.php';

$app = new WebApp;
if(!$app->init()){
	log_error('Can not initiate app');
	exit -1;
}
$app->run();

?>