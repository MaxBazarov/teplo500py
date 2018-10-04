from mako.template import Template
from Teplo500.utils import *

import WebApp

class AbstractPage:

	def compile_template(self, file_name, variables):
    
        ## extend variables
        variables ['sys_name'] = 'Teplo 500'

        app = app()
        
        if app.client:
            variables['sys_client_name'] = app.client.name
        variables['sys_baseurl'] = app.base_url()
        variables['sys_home_link'] = WebApp.HOME_SUBURL
        variables['sys_settings_link'] = WebApp.SETTINGS_SUBURL
        variables['sys_account_link'] = WebApp.ACCOUNT_SUBURL
        variables['sys_logout_link'] = WebApp.LOGOUT_SUBURL

        path_to_file = app.web_path()+'/Templates/'+file_name

        mytemplate = Template(filename=path_to_file)
        if not mytemplate:        
            log_error('AbstractPage: Template File not found: '+path_to_file)
            return None   
 
        return mytemplate.mytemplate.render_unicode(variables)


    def compile_page(self, file_name, variables):
        ## prep navigation
        variables['menu_'+app.page()+'_active'] = 'active'
        variables['layout_top'] = self.compile_template('layout_top.tmpl',variables)
        variables['layout_bottom'] = self.compile_template('layout_bottom.tmpl',variables)

        return self.compile_template(file_name,variables)
    
