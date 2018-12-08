import sys
sys.path.insert(1, "/Users/baza/Github/teplo500py/lib")
sys.path.insert(2, "/Users/baza/Github/teplo500py/web/code")

from flask import Flask

from teplo500web.web_app import *
from teplo500web.pages import settings_page
from teplo500web.pages import home_page
from teplo500web.pages import account_page
from teplo500web.pages import login_page
from teplo500web.rest import client_rest

flask_app = Flask(__name__)

home_page.home_page_register(flask_app)
settings_page.settings_page_register(flask_app)
account_page.account_page_register(flask_app)
login_page.login_page_register(flask_app)
client_rest.rest_register(flask_app)

if __name__ == '__main__':
    flask_app.run(debug=True)
