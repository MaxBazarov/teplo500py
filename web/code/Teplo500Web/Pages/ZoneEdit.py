from Teplo500.core import *
from Teplo500Web.web_core import *
import Teplo500.SalusZone
from Teplo500Web.Pages.AbstractPage import *
import time

class ZoneEdit(AbstractPage):
	def __init__(self):
		self.error_msg=''
		self.ok_msg=''

'''
class ZoneEdit extends AbstractPage
{
	private $error_msg='';
	private $name='';

	function show_page(){
		global $app;		


    	$vars = array(
    		'msg_header'=>locstr('Welcome to Teplo 500'),
    		'name'=>$this->email,
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
    		$app->set_client($client->id);
    		return $app->redirect_local(WebApp::HOME_SUBURL);
    		
    	}

    	return $this->show_page();
    }
 }

?>
'''