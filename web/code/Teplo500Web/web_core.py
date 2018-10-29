import cgi
from flask import make_response,request

from teplo500.core import *

def http_post_param(name,default=''):
	return request.form[name] if name in request.form else default

def http_get_param(name,default=''):
	return request.args.get(name,default)


