
def save_client_history(client):

	## PREPARE LOG FILE
	$date = new DateTime("now",new DateTimeZone('Europe/Moscow'));
	$time = $date->format('H:i');
	
	$path = $client->get_folder_path().'/history/'.$date->format('Y-m-d');


	$file_existed = file_exists($path);

	$file = fopen($path,'a');	
	if(!$file) return log_error('SalusClient: _save_history: can not file for append : '.$path);

	// WRITE TO FILE AT FIRST TIME
	if(!$file_existed){
		SalusHistoryHelper::_write_history_header($client,$file);
	}

	// START 
	fwrite($file,$time.';');

	// ask every device to save his state 
	foreach ($client->devices as $dev)
	{
		foreach ($dev->zones as $zone)
		{
			fwrite($file,$zone->current_temp.';');
			fwrite($file,$zone->current_mode_temp.';');
		}	
	}
	fwrite($file,"\n");
	fclose($file);

	return true;		

}

static function find_client_history($client,$date){
	$result = array(
		'prev_date'=>null,
		'next_date'=>null,
		'date'=>$date
	);
	$base_path = $client->get_folder_path().'/history/';
	$now = new DateTime('NOW');


	// check existing of data
	$path  = $base_path.$date->format('Y-m-d');
	if(!file_exists($path)) return false;		

	// date is not today (we are in the past)
	if(!$date->diff($now)==0){
		$next_date =  clone $date;
		$next_date->add(new DateInterval('P1D'));

		$path  = $base_path.$next_date->format('Y-m-d');
		if(file_exists($path)) $result['next_date'] = $next_date;
	}

	{
		$prev_date =  clone $date;
		$prev_date->sub(new DateInterval('P1D'));

		$path  = $base_path.$prev_date->format('Y-m-d');
		if(file_exists($path)) $result['prev_date'] = $prev_date;
	}


	return $result;

}

static function load_client_history($client,$date){
	$path = $client->get_folder_path().'/history/'.$date->format('Y-m-d');
	
	$handle = fopen($path, "r");
	if (!$handle) return false;

	$data = array(
		'header'=>array(),
		'records'=>array()
	);

	$buffer = fgets($handle, 4096);
	if( $buffer === false) return false;
	$header = explode(';',$buffer);
	array_pop($header);
	$data['header'] = $header;// drop last empty ;

    while (($buffer = fgets($handle, 4096)) !== false) {

    	$record = explode(';',preg_replace( "/\r|\n/", "", $buffer ));
    	array_pop($record); // drop last empty ;
        $data['records'][] = $record;
    }
    fclose($handle);
	
	return $data;

}


private  static function _write_history_header($client,&$file)
{
	fwrite($file,'time;');
	foreach ($client->devices as $dev)
	{
		foreach ($dev->zones as $zone)
		{
			$zone_name = $zone->name.'('.$dev->id.')';
			fwrite($file,$zone_name.'/Current Temperature;');
			fwrite($file,$zone_name.'/Auto Temperature;');
		}	
	}
	fwrite($file,"\n");
}

