from datetime import date, timedelta
import time,sys
import os.path

from Teplo500.core import *

def save_client_history(client):

	## PREPARE LOG FILE

	nowstr = time.strftime('%H:%M')	

	file_path = client.get_folder_path()+'/history/' + time.strftime(Constants.dateformat)	
	file_existed = os.path.isfile(file_path)

	log_debug('save_client_history() write to file: '+file_path)

	try:
		with open(file_path, 'a') as fp:		
			
			## WRITE TO FILE AT FIRST TIME
			if not file_existed:
				_write_history_header(client,fp)			

			## START 		
			fp.write(nowstr+';')			
			
			##ask every device to save his state 
			for dev in client.devices:		
				for zone in dev.zones:		
					fp.write(str(zone.current_temp)+';')
					fp.write(str(zone.current_mode_temp)+';')						
			fp.write("\n")						
	except OSError as err:
		log_error("save_client_history() {0}"+format(err))
		return False
	except:
		log_error("save_client_history(): Unexpected error:")		
		return False

	return True

## day: timestamp
def find_client_history(client,odate):

	result = {
		'prev_date':None,
		'next_date':None,
		'date':odate
	}

	base_path = client.get_folder_path()+'/history/'
	otoday = day_today()

	## check existing of data
	file_path  = base_path + day_str(odate)
	if not os.path.isfile(file_path):
		log_debug('find_client_history check path:'+file_path)		

	## date is not today (we are in the past)
	if (otoday-odate).days>0:
		next_date = odate + timedelta(days=1) 		
		next_file_path  = base_path + day_str(next_date)
		if os.path.isfile(next_file_path):
			result['next_date'] = next_date
	

	if True:
		prev_date = odate - timedelta(days=1) 		
		pref_file_path  =  base_path + day_str(prev_date)
		if os.path.isfile(pref_file_path):
			result['prev_date'] = prev_date

	return result



def load_client_history(client,date):

	file_path = client.get_folder_path()+'/history/'+ day_str(date)	
	
	result = {
		'header':[],
		'records':[]
	}

	if not os.path.isfile(file_path):
		result['status']='not_found'
		return result

	fp = open(file_path, 'r')
	counter = 0
	for line in fp:			
		if counter==0:
			## process first header line (drop last empty ;)					
			result['header'] = line.split(';')[0:-1]
		else:
			## process other lines
			rec = line.split(';')[0:-1]			
			result['records'].append( rec )
		counter+=1
	fp.close()	
	return result

def  _write_history_header(client,fp):

	fp.write('time;')
	for dev in client.devices:
		for zone in dev.zones:		
			zone_name = zone.name+'('+dev.id+')'
			fp.write(zone_name+'/Current Temperature;')
			fp.write(zone_name+'/Auto Temperature;')
			
	fp.write("\n")

	return True


