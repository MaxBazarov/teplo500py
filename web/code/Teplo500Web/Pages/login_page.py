from teplo500web.web_core import *
from teplo500 import core
from teplo500web.pages.abstract_page import AbstractPage

def login_page_register(flask):
    flask.add_url_rule('/login', 'login_page_show', login_page_show)
    flask.add_url_rule('/login/submit', 'login_page_submit', login_page_submit,methods=['POST'])
    return True

def login_page_show():
    page  = LoginPage()
    return core.app.create_response(page.show())	

def login_page_submit():
    page  = LoginPage()
    return core.app.create_response(page.submit())	

class LoginPage(AbstractPage):

    def __init__(self):
        super().__init__()
        self.email = ""

    def show(self):

        vars = {
            'error_msg': self.error_msg,
            'ok_msg':self.ok_msg,
            'email': self.email,
            'msg_header': locstr('Welcome to Teplo 500'),
            'form_url': "/login/submit",
        }

        return self.compile_page('login.tmpl',vars)


    def save(self):
        while(True):
                
            ## check Cancel button
            if http_post_param("save")=='': break
            
            client = core.app.client
            config = client.config
            
            ## check valid client
            if client is None:
                break

            ## read submitted data
            config['auto_update'] = http_post_param('auto_update').lstrip().rstrip()

            ##if(!is_numeric($config.auto_update)){
            ##	self.error_msg = locstr('The period should be a number.')
            ##	return self.edit()
            ##}           

            ## save new config
            if not client.save_config():
                self.error_msg = locstr('Failed to save settings')
                return self.show_edit()

            self.ok_msg = locstr('Settings succesfully updated.')
            break

        return self.show()


'''
class LoginPage extends AbstractPage
{
    private $error_msg='';
    private $email='';
    private $pswd='';

    function show_page(){
        global $app;		

        $app->login_helper->set_first_cookie();

        $vars = array(
            'msg_header'=>locstr('Welcome to Teplo 500'),
            'email'=>$this->email,
            'pswd'=>$this->pswd,
            'error_msg'=>$this->error_msg
        );

        $html = $this->compile_page('login.tmpl',$vars);
        echo $html;

        return true;
    }


    function run(){
        global $app;
        $submit = http_post_param('login');

        if($submit!=''){
            // READ SUBMITED FORM DATA
            $this->email = http_post_param('email');
            $this->pswd = http_post_param('password');    	

            // CHECK LOGIN 
            if($this->email==='' or $this->pswd===''){
                $this->error_msg = locstr('Both email and password should be specified.');
                return $this->show_page();
            }

            // TRY TO FIND CLIENT AND AUTORISE
            $client = SalusClient::Factory_CreateAndLoad($this->email);
            if(!$client or !$client->validate_password($this->pswd)){
                $this->error_msg = locstr('The email or password are wrong.');
                return $this->show_page();
            }

            // OK, AUTHORISED
            $app->save_login($client->id);
            return $app->redirect_local(WebApp::HOME_SUBURL);
            
        }

        return $this->show_page();
    }
 }

?>
'''