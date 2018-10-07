import cgi
from Teplo500.utils import *

def http_post_param(name):
	return ''
	#return cgi.escape(get_app().form.getfirst(name,''),True)

def http_get_param(name):
	return ''
	##if name not in get_app().get_params:
	###	return ''
	##return cgi.escape(get_app().get_params[name],True)


