from utils import *
from datetime import date
import time

## return WebLoginHelper instance or false(error) 
def def Create():
	helper = WebLoginHelper()
	if not helper.init():
		return log_error('WebLoginHelper::Factory_Create() can not init helper')
	return helper

class WebLoginHelper:

	def __init__(self):
		self.login_id = ''

	def init(self):
		return True


   	def set_first_cookie(self):
   		if self.login_id!='':
   			return True
   		self.set_cookie()
  	
 
   	def set_cookie(self,login_id=None):  		
   		if login_id is None:
   			self.login_id = uniqid()
   		else:
   			self.login_id = login_id
	

   		setcookie('login_id',self.login_id,int(time.time())+60*60*24*360)

   		return True
   	

   
   	private def _get_folder_path(self):
   		global $app;
		return $app->home_path().'/local/logins';		
   	}

	def logout()
	{
		global $app;
		if(self.login_id=='')	return True

		if(!self._delete_login_file()){
			return log_error('WebLoginHelper.logout() can not delete login file');
		}
		 
		return self.set_cookie(''); 
	}

	// return client_id or false
	def try_login()
	{
		$log_d = function($message){
			log_debug('WebLoginHelper: try_login(): '.$message);
		};

		$log_d('staring... ');

		// check filled cookie existing 
		if(array_key_exists('login_id',$_COOKIE)){
			self.login_id = clear_textid($_COOKIE['login_id']);		
		}
		$log_d('login_id='.self.login_id);
		if(self.login_id=='') return false;

		// check login file existing
		$file_path = self._path_to_login(self.login_id);
		if(!file_exists($file_path)) return false;

		// load login file
		$login = load_json_config($file_path,true);
		if(!$login){
			$log_d('can not load config '.$file_path);
			return false;
		}
		$client_id = $login['client_id'];
		
		$log_d('restored client_id='.$client_id );
		return $client_id;
	}


   	def save_login($client_id)
   	{
   		$log_d = function($message){
			log_debug('WebLoginHelper: save_login(): '.$message);
		};

   		//delete old login   		
   		if(!self._delete_login_file()) return log_error('WebLoginHelper.try_login() failed to delete old file');
   		$log_d('deleted old login_id='.self.login_id );
   		self.login_id = '';

   		// generate new login_id
   		self.login_id = uniqid();
   		$login = array(
   			'client_id'=>$client_id,
   			'last_client_ip'=>$_SERVER['REMOTE_ADDR'],
   			'last_time'=>time()
   		);
   		$log_d('generated new login_id='.self.login_id);

   		// save new login data to file
   		$file_path = self._path_to_login(self.login_id);
   		if(!save_json_config($file_path,$login)){
   			return log_error('WebLoginHelper: generate_login: failed to save in "'.$file_path.'"');
   		}
   		$log_d('saved new login to file='.$file_path);

   		// send new login id to client
  		self.set_cookie(self.login_id);
	
   		return True
   	}

   	private def _path_to_login($login_id){
   		return self._get_folder_path().'/'.$login_id.'.data';
   	}

   	private def _delete_login_file(self):
   		if(self.login_id==='') return True

   		// prepare to delete existing login
		$file_path = self._path_to_login(self.login_id);		
		if(file_exists($file_path)){
			if(!unlink($file_path)) return log_error('WebLoginHelper._delete_login_file() can not delete login file"'.$file_path.'"');
		}
		return True
   	}

}
?>
