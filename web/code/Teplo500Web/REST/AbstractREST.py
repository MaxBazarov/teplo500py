import Teplo500Web.WebApp

class AbstractREST:

	def __init__(self):
		Teplo500Web.WebApp.CreateAndInit()

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
