import sys
sys.path.insert(1, "/Users/baza/Github/teplo500py/lib")
sys.path.insert(2, "/Users/baza/Github/teplo500py/web/code")

from flask import Flask

from Teplo500Web.WebApp import *
from Teplo500Web.Pages.HomePage import *
from Teplo500Web.Pages.SettingsPage import *
from Teplo500Web.REST.ClientREST import *

flask_app = Flask(__name__)

home_page_register(flask_app)
settings_page_register(flask_app)
rest_register(flask_app)

if __name__ == '__main__':
    flask_app.run(debug=True)
