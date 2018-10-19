from Teplo500.core import *
from Teplo500Web.web_core import *
import Teplo500.SalusZone
from Teplo500Web.Pages.AbstractPage import *
import time

class AccountPage(AbstractPage):
	def __init__(self):
		self.error_msg=''
		self.ok_msg=''

'''
def AccountPage(AbstractPage):
{
	private $error_msg='';

	function show_page(){
		global $app;		

    	$vars = array(
            'logged_as'=>locstr('You signed in as {1}',$app->client->name),
    		'error_msg'=>$this->error_msg
    	);

    	$html = $this->compile_page('account.tmpl',$vars);
    	echo $html;

    	return true;
	}


    function run(){
    	global $app;
    	
    	return $this->show_page();
    }
 }

?>
'''