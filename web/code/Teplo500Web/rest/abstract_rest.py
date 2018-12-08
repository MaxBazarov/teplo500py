
from teplo500web import web_app

class AbstractREST:

	def __init__(self):
		web_app.CreateAndInit()

	def run(self):
		return True

	def show_non_auth_error(self):
		return '401'

	def ShowUknownCmd(self):
		return '403'

	def ShowNoData(self):
		return '404'

	def ShowError(self):		
		return '500'
