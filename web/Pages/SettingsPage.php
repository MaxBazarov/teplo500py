<?php


class SettingsPage extends AbstractPage
{
	private $error_msg='';

	function show_page(){
		global $app;		
        $client = $app->client;


    	$vars = array(
    		'error_msg'=>$this->error_msg,
            'client'=>$app->client,
    	);

    	$html = $this->compile_page('settings.tmpl',$vars);
    	echo $html;

    	return true;
	}

    function show_edit_auto(){
        global $app;        
        $client = $app->client;

        $vars = array(            
            'error_msg'=>$this->error_msg,
            'ok_msg'=>$this->ok_msg,
            'form_url'=>WebApp::SETTINGS_SUBURL.'&cmd=save_auto',
            'auto_update'=>$client->get_auto_update()
        );

        $html = $this->compile_page('settings_edit_auto.tmpl',$vars);
        echo $html; 

        return true;
    }

     function do_save_auto(){
        while(true){
            // check Cancel button
            if( http_post_param("save")=='') break;

            global $app;
            $client = $app->client;
            $config = $client->config;
            
            // check valid client
            if(!$client) break;

            // read submitted data
            $config->auto_update = ltrim(rtrim(http_post_param('auto_update')));
            if(!is_numeric($config->auto_update)){
                $this->error_msg = locstr('The period should be a number.');
                return $this->show_edit_auto();  
            }           

            // save new config
            if(!$client->save_config()){
                $this->error_msg = locstr('Failed to save settings');
                return $this->show_edit_auto();
            }

            $this->ok_msg = locstr('Succesfully updated.');
            break;
        }

        return $this->show_page();

    }


    function run(){
        global $app;
    	$cmd = http_get_param("cmd");
        log_debug('SettingsPage: run: cmd="'.$cmd.'"');
        
        switch($cmd){            
            // =========== AUTO_UPDATE  ====
            case 'edit_auto':
                return $this->show_edit_auto();
            case 'save_auto':                
                return $this->do_save_auto();
        }

        return $this->show_page();
    }
 }

?>
