import os.path
from mako.template import Template
from Teplo500.utils import *

TEMPLATES_FOLDER = '/system/email_templates'
EMAILS_FOLDER = '/local/logs/emails'


class EmailTemplate:
    
    def __init__(self, template_name):
        self.variables = {}
        self.path_to_file= ''
        self.template_name = template_name


    def __set(self, key, val):
        self.variables[key] = val
    

    def _compile(self, file_name_postfix):
        path_to_file = app.home_path() + TEMPLATES_FOLDER + '/' + self.template_name + file_name_postfix+'.'+app.lang

        mytemplate = Template(filename=path_to_file)
        if not mytemplate:        
            log_error('AbstractPage: Template File not found: '+path_to_file)
            return None   
 
        return mytemplate.mytemplate.render_unicode(self.variables)
    
    def compile_body(self):
        return self._compile('_body')
    

    def compile_subject(self):
        return this._compile('_subject')

class Emailer:

    def __construct(self,to):    
        self.template = None
        self.template_subject = None

        self.recipients = {
            to:to ##1 Recip        
        }
    

    def set_template(self, template):
        self.template = template
    

    def send(self):     
        subject = self.template.compile_subject()
        body = self.template.compile_body()

        ## SEND REAL EMAIL USING GMAIL
        gmail = app.config['gmail']
        if gmail['enabled']:
            ## TODO: link to some emailer
            ## gmail['auth_name']            
            ## gmail['auth_key']
            ## subject
            ## self.recipients
            ## body 

            log_ok('Emailer: send : sent ok');
        
        return True
