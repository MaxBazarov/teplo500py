#import urllib.parse as urlparse
#import cgitb
#import cgi
import os.path
import sys
import json
from datetime import date

from flask import make_response,request
from flask import redirect


from teplo500web.web_core import *
from teplo500.core import *
from teplo500 import core
from teplo500.salus import salus_client
from teplo500.abstract_app import AbstractApp
from teplo500.salus import salus_connect
from teplo500web import web_login_helper


def InitBeforeRequest():
    CreateAndInit()
    log_debug('login_check')
    if core.app.client:
        return None    
    if core.app.page=='login':
        return None
    return core.app.redirect_to_login()


def CreateAndInit():
    wa = WebApp()
    if not wa.init():
        return None            
    return wa


class WebApp(AbstractApp):

    def __init__(self):
        super().__init__()

        self.client = None
        self.login_helper = None
        self.rest_page = None

        self.client_id = ''
        self.page = ''

        self.urls = {
            'ORG_SITE' : 'https://teplo500.ru',
            'LOGIN_SUBURL' : '/login',
            'LOGOUT_SUBURL' : '/logout',
            'HOME_SUBURL' : '/home',
            'SETTINGS_SUBURL' : '/settings',
            'ACCOUNT_SUBURL' : '/account'
        }        

        self.new_cookies = []
            
    
    def init(self):
        if not super().init(): return False

        log_debug("full_path="+request.full_path)
        page = request.full_path.replace("?","/").split("/")[1]
        self.page = page if page!="" else "home"

        ## check files
        messages_path = self._messages_log_path()

        ## create messages log file if it doesn't exist
        if not os.path.isfile(messages_path):
            fp = open(messages_path, 'w')
            fp.close()
                        
        ## prepare login cookie management helper
        self.login_helper = web_login_helper.Create()
        if not self.login_helper:
            return log_error('WebApp: init(): can not create login helper')

        client_id = self.login_helper.try_login()
        if client_id!='':
            self.client = salus_client.CreateAndLoad(client_id)
            log_debug("WebApp.init() tried to init client with ID:"+str(client_id))
            if self.client:
                log_debug("WebApp.init() inited client")
                self.client_id = client_id
        else:
            log_debug("WebApp.init() client_id is empty")  
        
        ## switch salus mode
        self.salus.set_mode(salus_connect.MODE_REAL if self.config['web']['salus_mode']=='real' else salus_connect.MODE_EMUL)
            
        return True

    def set_cookie(self,key,value,max_age):
        self.new_cookies.append({
            'key':key,
            'value':value,
            'max_age':max_age
        })


    def get_client_id(self):
        return self.client_id

    def save_login(self,client_id):
        if client_id=='':
            return False
        self.client_id = client_id
        self.client = salus_client.CreateAndLoad(self.client_id);
        self.login_helper.save_login(client_id)
        return True

    def save_logout(self):
        self.login_helper.logout()
        self.client = None
        self.client_id = '';              
        return True

    def web_path(self):
        return self.home_path()+'/web'
    

    def page(self):
        return self.page
    
    def base_url(self):
        return self.config['web']['base_url']
    
    def redirect(self,url):
        return redirect(url)

    def redirect_local(self,suburl):
        return self.redirect(self.base_url()+suburl)

    def redirect_to_login(self):
        self.save_logout()

        login_url = self.base_url() + self.urls['LOGIN_SUBURL']
        return self.redirect(login_url)
        

    def _messages_log_path(self):    
        return self.home_path()+'/local/logs/messages.log'
    
    
    def log_text(self, level, text1, text2=''):
        stime = datetime.now().strftime('%y-%m-%d %H:%M:%S')    

        prefixes={
            Log.OK:' [OK ] ',
            Log.ERR:' [ERR ] ',
            Log.DBG:' [DBG ] '
        }

        fp = open(self._messages_log_path(),  encoding='utf-8', mode='a')
        fp.write('['+stime+']'+ prefixes[level] + text1 + text2 +"\n")
        fp.close()

        return True

    def create_response(self,content):
        response = make_response(content)
        for cookie in self.new_cookies:            
            response.set_cookie(cookie['key'], cookie['value'],cookie['max_age'])
        return response
