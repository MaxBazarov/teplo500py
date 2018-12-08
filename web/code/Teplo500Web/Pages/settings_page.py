import time

from teplo500web.web_core import *
from teplo500 import core
from teplo500web.pages.abstract_page import AbstractPage

def settings_page_register(flask):
	flask.add_url_rule('/settings', 'settings_page_show', settings_page_show)
	flask.add_url_rule('/settings/edit', 'settings_page_edit', settings_page_edit)
	flask.add_url_rule('/settings/save', 'settings_page_save', settings_page_save,methods=['POST'])
	return True


def settings_page_show():
	page  = SettingsPage()
	return core.app.create_response(page.show())	

def settings_page_edit():
	page  = SettingsPage()
	return core.app.create_response(page.edit())

def settings_page_save():
	page  = SettingsPage()
	return core.app.create_response(page.save())	

class SettingsPage(AbstractPage):
	def show(self):
		client = core.app.client

		vars = {
			'error_msg':self.error_msg,
			'ok_msg':self.ok_msg,
			'client':client
		}

		return self.compile_page('settings.tmpl',vars)


	def edit(self):
		client = core.app.client

		vars = {
			'error_msg': self.error_msg,
			'ok_msg':self.ok_msg,
			'form_url': core.app.urls['SETTINGS_SUBURL']+"/save",
            'auto_update': client.get_auto_update()
		}

		return self.compile_page('settings_edit_auto.tmpl',vars)


	def save(self):
		while(True):
				
			## check Cancel button
			if http_post_param("save")=='': break
			
			client = core.app.client
			config = client.config
			
			## check valid client
			if client is None:
				break

			## read submitted data
			config['auto_update'] = http_post_param('auto_update').lstrip().rstrip()

			##if(!is_numeric($config.auto_update)){
			##	self.error_msg = locstr('The period should be a number.')
			##	return self.edit()
			##}           

			## save new config
			if not client.save_config():
				self.error_msg = locstr('Failed to save settings')
				return self.show_edit()

			self.ok_msg = locstr('Settings succesfully updated.')
			break

		return self.show()
