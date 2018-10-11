import sys
sys.path.insert(1, "/Users/baza/Github/teplo500py/lib")
sys.path.insert(2, "/Users/baza/Github/teplo500py/web/code")

from flask import Flask

from Teplo500Web.WebApp import *
from Teplo500Web.Pages.HomePage import *

flask_app = Flask(__name__)

homepage_register(flask_app)

'''
@flask_app.route("/")
def index():
    webapp = WebApp()
    if not webapp.init():
        log_error('Can not initiate app')
        exit(-1)
    return webapp.run()
''' 

if __name__ == '__main__':
    flask_app.run(debug=True)
