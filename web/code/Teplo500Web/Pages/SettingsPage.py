import time

from Teplo500Web.web_core import *
import teplo500.SalusZone
import teplo500.core as core
import Teplo500Web.Pages.abstract_page

def settings_page_register(flask):
	flask.add_url_rule('/settings', 'settings_page_show', settings_page_show)
	flask.add_url_rule('/settings/edit', 'settings_page_edit', settings_page_edit)
	flask.add_url_rule('/settings/save', 'settings_page_save', settings_page_save)
	return True


def settings_page_show():
	return core.app.create_response( 
		SettingsPage().show()
	)

def settings_page_edit():
	return core.app.create_response( 
		SettingsPage().edit()
	)

def settings_page_save():
	return core.app.create_response( 
		 SettingsPage().save()
	)

class SettingsPage(AbstractPage):
	def __init__(self):
		super().__init__()
		self.error_msg=''
		self.ok_msg=''	

	def show(self):
		client = core.app.client

		vars = {
			'error_msg':self.error_msg,
			'ok_msg':self.ok_msg,
			'client':client
		}

		return self.compile_page('settings.tmpl',vars)


	def edit(self):
		client = core.app.client

		vars = {
			'error_msg': self.error_msg,
			'ok_msg':self.ok_msg,
			'form_url': core.app.urls['SETTINGS_SUBURL']+"/save",
            'auto_update': client.get_auto_update()
		}

		return self.compile_page('settings_edit_auto.tmpl',vars)


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
			config['auto_update'] = http_post_param('auto_update').lstrip().rstip()

			##if(!is_numeric($config.auto_update)){
			##	self.error_msg = locstr('The period should be a number.')
			##	return self.edit()
			##}           

			## save new config
			if not client.save_config():
				self.error_msg = locstr('Failed to save settings')
				return self.show_edit()

			self.ok_msg = locstr('Succesfully updated.')
			break

		return self.show()



'''
class SettingsPage extends AbstractPage
{
	private $error_msg='';

	function show_page(){
		global $app;		
        $client = $app.client;


    	$vars = array(
    		'error_msg':self.error_msg,
            'client':app.client,
    	);

    	$html = $self.compile_page('settings.tmpl',$vars);
    	echo $html;

    	return true;
	}

    function show_edit_auto(){
        global $app;        
        $client = $app.client;

        $vars = array(            
            'error_msg':self.error_msg,
            'ok_msg':self.ok_msg,
            'form_url'=>WebApp::SETTINGS_SUBURL.'&cmd=save_auto',
            'auto_update':client.get_auto_update()
        );

        $html = $self.compile_page('settings_edit_auto.tmpl',$vars);
        echo $html; 

        return true;
    }

     function do_save_auto(){
        while(true){
            // check Cancel button
            if( http_post_param("save")=='') break;

            global $app;
            $client = $app.client;
            $config = $client.config;
            
            // check valid client
            if(!$client) break;

            // read submitted data
            $config.auto_update = ltrim(rtrim(http_post_param('auto_update')));
            if(!is_numeric($config.auto_update)){
                $self.error_msg = locstr('The period should be a number.');
                return $self.show_edit_auto();  
            }           

            // save new config
            if(!$client.save_config()){
                $self.error_msg = locstr('Failed to save settings');
                return $self.show_edit_auto();
            }

            $self.ok_msg = locstr('Succesfully updated.');
            break;
        }

        return $self.show_page();

    }


    function run(){
        global $app;
    	$cmd = http_get_param("cmd");
        log_debug('SettingsPage: run: cmd="'.$cmd.'"');
        
        switch($cmd){            
            // =========== AUTO_UPDATE  ====
            case 'edit_auto':
                return $self.show_edit_auto();
            case 'save_auto':                
                return $self.do_save_auto();
        }

        return $self.show_page();
    }
 }

?>
'''