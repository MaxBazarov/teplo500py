# coding=latin-1
import requests
import os.path
from enum import Enum
from time import time
import json	

app = None

# DEFINE CONSTANTS
class Log(Enum):
	OK = 1 
	DBG = 2
	ERR = 3

## ========================== LOCALISATION =========================== 
## localise string
def locstr(str, param1=None, param2=None, param3=None):
	str = app.translate_string(str)

	if param1 is not None:
		str = str_replace('{1}',param1,str)
		if param2 is not None:
			str = str_replace('{2}',param2,str)
			if param3 is not None:
				str = str_replace('{3}',param3,str);
	return str;


def choose(check,value1,value2):
	if check:
		return value1
	else:
		return value2

## ========================== LOW LEVEL LIBRARY =========================== 
def temp_to_str(temp):	
	if temp==0:
		return '0°'
	elif temp>0:
		return str(temp) + '°'
	else:
		return str(temp) + '°'
	
def c():    
    return hex(int(time()*10000000))[2:]

##  ========================== LOW LEVEL LIBRARY =========================== 
def time_diff(start_time, end_time = None):
	'''
	start = new DateTime(); 
	start->setTimestamp($start_time);
	$end = new DateTime("now");
	if$end_time) $end->setTimestamp($end_time);


    $interval = $end->diff($start); 
    
    $format = array(); 
    if($interval->y !== 0) { 
        $format[] = "%y ".locstr('year(s)/timediff'); 
    } 
    if($interval->m !== 0) { 
        $format[] = "%m ".locstr('month(s)/timediff'); 
    } 
    if($interval->d !== 0) { 
        $format[] = "%d ".locstr('day(s)/timediff'); 
    } 
    if($interval->h !== 0) { 
        $format[] = "%h ".locstr('hour(s)/timediff'); 
    } 
    if($interval->i !== 0) { 
        $format[] = "%i ".locstr('minute(s)/timediff'); 
    } 
    if($interval->s == 0  and !count($format)) {
    	 return locstr('Updated right now/timediff');
    } 
    if($interval->s !== 0  and !count($format)) {
    	 return locstr('Updated less than a minute ago/timediff');
    }
    if($interval->s !== 0) { 
        $format[] = "%s ".locstr('second(s)/timediff');       
    } 
    
    // We use the two biggest parts 
    if(count($format) > 1) { 
        $format = locstr('Updated: {1} and {2}/timediff',array_shift($format),array_shift($format) );
    } else { 
        $format = locstr('Updated: {1}/timediff',array_pop($format));
    } 
    
    // Prepend 'since ' or whatever you like 
    return $interval->format($format); 
}
	'''
	return 0


def clear_textid(id):
	id = id.replace('\\','')
	id = id.replace('/','')
	id = id.replace('.','')
	return id


def save_json_config(file_path, data):	

	try:
		with open(file_path, 'w') as fp:
			json.dump(data,fp,sort_keys=False, indent=4)
	except OSError as err:
		log_error("save_json_config() {0}".format(err))
		return False
	except:
		log_error("save_json_config(): Unexpected error:"+sys.exc_info()[0])		
		return False

	return 	True


def load_json_config(file_path):

	if not os.path.isfile(file_path):
		log_error("load_json_config(): No such file "+file_path)
		return None
	
	try:
		with open (file_path, 'r') as fp:
			config = json.load(fp)
	except OSError as err:
		log_error("load_json_config(): {0}".format(err))
		return None
	except:
		log_error("load_json_config(): Unexpected error:"+sys.exc_info()[0])		
		return None

	return config


def log_text(level, text1, text2=''):
	app.log_text(level, text1, text2)
	return True

def log_error(text1):
	log_text(Log.ERR, text1)
	return False ## special result to use it in code like :       $file = fopen(); if(!$file) return log_error('ERROR!!!!');


def log_ok(text1):
	log_text(Log.OK, text1)
	return True


def log_debug(text1):
	log_text(Log.DBG, text1)
	return True

'''
/**
TODO: REPLACE FUNCTION
from http://php.net/manual/ru/function.file-get-contents.php#102575
make an http POST request and return the response content and headers
@param string $url    url of the requested script
@param array $data    hash array of request variables
@return returns a hash array with response content and headers in the following form:
    array ('content'=>'<html></html>'
        , 'headers'=>array ('HTTP/1.1 200 OK', 'Connection: close', ...)
        )
*/

'''

##import urllib2,cookielib


## see details here -http://docs.python-requests.org/en/master/user/quickstart/
## return req
##		.text
##		.cookies
##		.headers
def net_http_request(url,referer,data,method,PHPSESSID):

	log_debug('net_http_request(): url = '+url)


	UserAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Safari/604.1.38';

	headers = {
		"Connection":"close",
		"Host" : "salus-it500.com",
		"Origin" : "https://salus-it500.com",
		"Referer" : referer,
		"Location" :  referer,
		"User-Agent" : UserAgent,
	}

	cookies = {}

	if PHPSESSID!='':
		cookies['PHPSESSID'] = PHPSESSID

	if method=='GET':
		headers["Content-Type"] = "text/html"
		headers['charset'] = "utf-8"

		###header = header + "Content-Length: "+data_len+"\r\n";
		req = requests.get(url,headers=headers,cookies=cookies)
		
	else:
		headers["Content-type"] = "application/x-www-form-urlencoded"

		req = requests.post(url,data = data,headers=headers,cookies=cookies)
	
	return req



import time

def uniqid(prefix = ''):
    return prefix + hex(int(time()))[2:10] + hex(int(time()*1000000) % 0x100000)[2:7]


'''
TODO: REPLACE FUNCTIONS
function date_str($date){
	return $date?$date->format('Y-m-d'):'';
}

function date_txt($date){
	return $date?$date->format('d-m-Y'):'';
}
'''