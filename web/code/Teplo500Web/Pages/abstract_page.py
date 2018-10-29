from mako.template import Template
from teplo500.core import *

import Teplo500Web.WebApp

class AbstractPage:

    def __init__(self):
        Teplo500Web.WebApp.CreateAndInit()


    def compile_template(self, file_name, variables):
    
        ## extend variables
        variables['sys_name'] = 'Teplo 500'

        a = get_app()
        
        if a.client:
            variables['sys_client_name'] = a.client.name
        variables['sys_baseurl'] = a.base_url()
        variables['sys_home_link'] = a.urls['HOME_SUBURL']
        variables['sys_settings_link'] = a.urls['SETTINGS_SUBURL']
        variables['sys_account_link'] = a.urls['ACCOUNT_SUBURL']
        variables['sys_logout_link'] = a.urls['LOGOUT_SUBURL']

        path_to_file = a.web_path()+'/Templates/'+file_name

        mytemplate = Template(filename=path_to_file,input_encoding='utf-8',output_encoding='utf-8',strict_undefined=True)
        if not mytemplate:        
            log_error('AbstractPage: Template File not found: '+path_to_file)
            return None   
 
        return mytemplate.render_unicode(**variables)


    def compile_page(self, file_name, variables):
        a = get_app()
        ## prep navigation        
        variables['page'] = a.page
        ##variables['menu_home_active'] = ''
        ##variables['menu_account_active'] = ''
        ##variables['menu_'+a.page+'_active'] = 'active'
        if not 'sys_body_custom' in variables: variables['sys_body_custom']=''
        if not 'sys_head_custom' in variables: variables['sys_head_custom']=''
            
        variables['layout_top'] = self.compile_template('layout_top.tmpl',variables)
        variables['layout_bottom'] = self.compile_template('layout_bottom.tmpl',variables)

        return self.compile_template(file_name,variables)
    
