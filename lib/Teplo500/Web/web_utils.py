import cgi

def http_post_param(name):
	return cgi.escape(app.form.getfirst(name,''),True)

def http_get_param(name):
	if name not in app.get_params:
		return ''
	return cgi.escape(app.get_params[name],True)


