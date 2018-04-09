from datetime import date
import os.path


def save_client_history(client):

	## PREPARE LOG FILE

	date = datetime.now()
	time = date.strftime('%H:%M')	

	file_path = client.get_folder_path()+'/history/' + date.strftime('%y-%m-%d')	
	file_existed = os.path.isfile(file_path)

	try:
		with open(file_path, 'a') as fp:
		
		## WRITE TO FILE AT FIRST TIME
		if not file_existed:
			_write_history_header(client,fp)			

		## START 		
		fp.write(time+';')

		##ask every device to save his state 
		for dev in client.devices:		
			for zone in dev.zones:		
				fp.write(zone.current_temp+';')
				fp.write(zone.current_mode_temp+';')				
		
		fp.write("\n")

	except OSError as err:
		log_error("save_client_history() {0}".format(err))
		return False
	except:
		log_error("save_client_history(): Unexpected error:"+sys.exc_info()[0])		
		return False

	return True

def  function find_client_history(client,date):

	result = {
		'prev_date':None,
		'next_date':None,
		'date':date
	}

	base_path = client.get_folder_path()+'/history/';
	now = datetime.now()

	## check existing of data
	file_path  = base_path + date.strftime('%y-%m-%d')
	if not os.path.isfile(file_path):
		return False

	## date is not today (we are in the past)
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


	return result



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

