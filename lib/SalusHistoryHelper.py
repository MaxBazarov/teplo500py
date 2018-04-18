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

def function find_client_history(client,date):

	result = {
		'prev_date':None,
		'next_date':None,
		'date':date
	}

	base_path = client.get_folder_path()+'/history/'
	now = datetime.now()

	## check existing of data
	file_path  = base_path + date.strftime('%y-%m-%d')
	if not os.path.isfile(file_path):
		return False

	## date is not today (we are in the past)
	if (now-date).days>0:
		next_date = date + datetime.timedelta(days=1) 		

		next_file_path  = base_path + next_date.strftime('%y-%m-%d')
		if os.path.isfile(next_file_path):
			result['next_date'] = next_date
	

	if True:
		prev_date = date - datetime.timedelta(days=1) 		
		pref_file_path  =  base_path + prev_date.strftime('%y-%m-%d')
		if os.path.isfile(pref_file_path):
			result['prev_date'] = prev_date

	return result



def function load_client_history(client,date):

	file_path = client.get_folder_path()+'/history/'+ date.strftime('%y-%m-%d')
	
	result = {
		'header':[],
		'records':[]
	}

	try:
		with open(file_path, 'r') as fp:		
			counter = 0
			for line in fp:			
				if counter==0:
					## process first header line (drop last empty ;)					
					data['header'] = line.split(':').pop()
				else:
					## process other lines
					data['records'].append( line.split(':').pop() )
				counter++

			return result
	except OSError as err:
		log_error("load_client_history() {0}".format(err))
		return None
	except:
		log_error("load_client_history(): Unexpected error:"+sys.exc_info()[0])		
		return None

	return None

def function _write_history_header(client,fp):

	fp.write('time;')
	for dev in client.devices:
		for zone in dev.zones:		
			zone_name = zone.name+'('+dev.id+')'
			fp.write(zone_name+'/Current Temperature;')
			fp.write(zone_name+'/Auto Temperature;')
			
	fwrite(file,"\n")

	return True


