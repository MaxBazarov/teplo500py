class AbstractREST:

	def run():
		return True

	def show_non_auth_error():
		print('401')
		return False

	def ShowUknownCmd():
		print('404')
		return True

	def ShowNoData():
		print('404')
		return False

	def ShowError():
		print('403')
		return False
