import sys
import requests
import os.path
from enum import Enum
from time import time
from datetime import date
from datetime import datetime
import json	

app = None

def get_app():
	return app

# DEFINE CONSTANTS
class Log(Enum):
	OK = 1 
	DBG = 2
	ERR = 3


class Constants:
	dateformat = '%Y-%m-%d'
	dateformat_txt = '%d-%m-%Y'

## ========================== LOCALISATION =========================== 
## localise string
def locstr(str, param1=None, param2=None, param3=None):
	str = app.translate_string(str)

	if param1 is not None:
		str = str.replace('{1}',param1)
		if param2 is not None:
			str = str.replace('{2}',param2)
			if param3 is not None:
				str = str.replace('{3}',param3)
	return str


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
		return str(temp) + u'\N{DEGREE SIGN}'
	else:
		return str(temp) + u'\N{DEGREE SIGN}'
	
def c():    
    return hex(int(time()*10000000))[2:]

class MyInterval:
	def __init__(self,interval):
		self.years = int(round(interval.days/365))
		self.months = 0
		self.days = interval.days
		self.hours = int(round(interval.seconds/3600))
		self.minutes = 0
		self.seconds = interval.seconds
		###
		self.days = self.days - self.years*365
		self.months = int(round(self.days/30.5))
		self.days = self.days - int(self.months*30.5)

		self.seconds = self.seconds - self.hours*3600		
		self.minutes = int(round(self.seconds/60))
		self.seconds = self.seconds - self.minutes*60		
		

	def get_txt(self):
		formats = []

		if self.years: formats.append("%y "+locstr('year(s)/timediff'))
		if self.months: formats.append( "%M "+locstr('month(s)/timediff')) 
		if self.days: formats.append("%d "+locstr('day(s)/timediff')) 
		if self.hours: formats.append("%h "+locstr('hour(s)/timediff')) 	
		if self.minutes: formats.append("%m "+locstr('minute(s)/timediff')) 
		if self.seconds == 0  and not formats: return locstr('Updated right now/timediff')   	
		if self.seconds != 0  and not formats: return locstr('Updated less than a minute ago/timediff')
		if self.seconds != 0: formats.append("%s "+locstr('second(s)/timediff')) 

		log_debug(str(formats))

		## We use the two biggest parts 
		formats.reverse()
		if len(formats) > 1:
			format = locstr('Updated: {1} and {2}/timediff',formats.pop(),formats.pop() )
		else:
			format = locstr('Updated: {1}/timediff',formats.pop())

		res_str = format.replace("%s",str(int(self.seconds))).replace("%m",str(int(self.minutes))).replace("%h",str(int(self.hours)))
		res_str = res_str.replace("%d",str(int(self.days))).replace("%M",str(int(self.months))).replace("%y",str(int(self.years)))

		return res_str

	
##  ========================== LOW LEVEL LIBRARY =========================== 
## get time in unixtimestmp format (secs)
def time_diff(start_time, end_time = None):	
	
	start = datetime.fromtimestamp(start_time)
	end = datetime.now() if end_time is None else datetime.fromtimestamp(end_time)

	interval = end - start
	res = MyInterval(interval)

	return res.get_txt()

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
		log_error("save_json_config() {0}"+format(err))
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
		log_error("load_json_config(): {0}"+format(err))
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
	return False ## special result to use it in code like :       $file = fopen(); if(!$file) return log_error('ERROR!!!!')


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
def net_http_request(url,referer,data,method,PHPSESSID='',content_type=''):

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
		headers["Content-Type"] = "text/html" if content_type=='' else content_type
		headers['charset'] = "utf-8"

		###header = header + "Content-Length: "+data_len+"\r\n";
		req = requests.get(url,headers=headers,cookies=cookies)
		
	else:
		headers["Content-type"] = "application/x-www-form-urlencoded" if content_type=='' else content_type
		req = requests.post(url,data = data,headers=headers,cookies=cookies)
	
	return req



import time

def uniqid(prefix = ''):
    return prefix + hex(int(time()))[2:10] + hex(int(time()*1000000) % 0x100000)[2:7]

def day_today():
	return date.today()

def date_now_txt():
	return day_today().strftime(Constants.dateformat_txt)

## result: datetime.date
def str_date(day_str):
	return date.fromisoformat(day_str)

## day: datetime.date
def day_str(day):
	if day is None:  return ''

	if isinstance(day,int):
		day = datetime.fromtimestamp(day)
	elif isinstance(day,str):		
		day = str_date(day)

	return day.strftime(Constants.dateformat)	

## day: datetime.date
def day_txt(day):
	if day is None:  return ''			
	return day.strftime(Constants.dateformat_txt)	
