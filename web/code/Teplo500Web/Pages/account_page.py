from teplo500web.web_core import *
from teplo500 import core
from teplo500web.pages.abstract_page import AbstractPage

def account_page_register(flask):
	flask.add_url_rule('/account', 'account_page_show', account_page_show)
	flask.add_url_rule('/logout', 'account_page_do_logout', account_page_do_logout)
	return True

def account_page_show():
	page  = AccountPage()
	return core.app.create_response(page.show())	

def account_page_do_logout():
	page  = AccountPage()
	return core.app.create_response(page.do_logout())	


class AccountPage(AbstractPage):
	def show(self):
		client = core.app.client

		vars = {
			'error_msg':self.error_msg,
			'logged_as':locstr('You signed in as {1}',client.name)
		}

		return self.compile_page('account.tmpl',vars)

	def do_logout(self):
		return core.app.redirect_to_login()
