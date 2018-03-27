<?php


class HomePage extends AbstractPage
{
	public $error_msg='';
    public $ok_msg='';


	function show_page(){
		global $app;		
        
        // SHOW DEVICES+ZONES

        $devices_html = '';
        $counter = 0;
        $esm = false;
        foreach($app->client->devices as $device){            
            $zones_html = '';          
            foreach(array_reverse($device->zones) as $zone){
                if($zone->is_esm()) $esm = true;
                $vars = array(
                    'zone'=>$zone
                );
                $zones_html.=$this->compile_template('home_zone.tmpl',$vars);
            }
            $vars = array(
                'device'=>$device,
                'counter'=>$counter,
                'devices_total'=>count($app->client->devices),
                'zones_html'=>$zones_html
            );
            $devices_html.=$this->compile_template('home_device.tmpl',$vars);
            $counter++;
        };

        // SHOW CHARTS
        $chart_html = '';  
        {
            $vars = array(
                'date'=>new DateTime("now")
            );
            $chart_html = $this->compile_template('home_chart.tmpl',$vars);            
        }

    	$vars = array(            
    		'error_msg'=>$this->error_msg,
            'ok_msg'=>$this->ok_msg,
            'home_update_link'=>WebApp::HOME_SUBURL.'&cmd=update',
            'home_switch_esm_link'=>WebApp::HOME_SUBURL.'&cmd='.($esm?'disable_esm':'enable_esm'),
            'home_switch_esm_text'=>$esm?locstr('Disable Energy Save'):locstr('Enable Energy Save'),
            'updated_raw'=>$app->client->data_updated_time,
            'updated_text'=>date("M d H:i:s",$app->client->data_updated_time),
            'devices_html'=>$devices_html,
            'chart_html'=>$chart_html,
            'sys_head_custom' => $this->compile_template('home_head.tmpl',array()),
            'sys_body_custom' => ''
    	);

    	echo $this->compile_page('home.tmpl',$vars);    	

    	return true;
	}


    function show_edit_zone_temp($zone=false){
        global $app;        
        $client = $app->client;
        $zone = $zone?$zone:$this->_get_current_zone();

        if(!$zone) return $this->show_page(); 


        // define temperature range 
        $temps = array();
        for($t=30;$t>=5;$t-=0.5){ $temps[] = $t; }

        $vars = array(            
            'error_msg'=>$this->error_msg,
            'ok_msg'=>$this->ok_msg,
            'temps'=>$temps,
            'form_url'=>WebApp::HOME_SUBURL.'&cmd=save_zone_temp&zone_id='.$zone->id,            
            'man_temp'=>($zone->mode==SalusZone::MODE_AUTO or $zone->mode==SalusZone::MODE_MAN)?$zone->current_mode_temp:$zone->current_temp,
            'name'=>$zone->name
        );

        $html = $this->compile_page('home_edit_zone_temp.tmpl',$vars);
        echo $html;

        return true;
    }

    
    function do_save_zone_temp(){
        while(true){
            // check Cancel button
            if( http_post_param("save")=='') break;

            global $app;
            $client = $app->client;
            $zone = $this->_get_current_zone();
            
            // check valid client id
            if(!$zone) break;

            // read submitted data
            $new_man_temp = ltrim(rtrim(http_post_param('man_temp')));
            if($new_man_temp==''){
                $this->error_msg = locstr('New temperature should be specified.');
                return $this->show_edit_zone($zone); 
            }

            // save new data
            

            $this->ok_msg = locstr('Succesfully completed.');
            break;
        }

        return $this->show_page();

    }


    function show_edit_zone($zone=false){
        global $app;        
        $client = $app->client;
        $zone = $zone?$zone:$this->_get_current_zone();

        if(!$zone) return $this->show_page(); 

        $vars = array(            
            'error_msg'=>$this->error_msg,
            'ok_msg'=>$this->ok_msg,
            'form_url'=>WebApp::HOME_SUBURL.'&cmd=save_zone&zone_id='.$zone->id,
            'name'=>$zone->name
        );

        $html = $this->compile_page('home_edit_zone.tmpl',$vars);
        echo $html;

        return true;
    }

    function do_save_zone(){
        while(true){
            // check Cancel button
            if( http_post_param("save")=='') break;

            global $app;
            $client = $app->client;
            $zone = $this->_get_current_zone();
            
            // check valid client id
            if(!$zone) break;

            // read submitted data
            $zone->name = ltrim(rtrim(http_post_param('name')));
            if($zone->name==''){
                $this->error_msg = locstr('Name should be specified.');
                return $this->show_edit_zone($zone); 
            }

            // save new data
            if(!$client->save_data()){
                $this->error_msg = locstr('Failed to save updated data.');
                return $this->show_edit_zone($zone);    
            }

            $this->ok_msg = locstr('Succesfully updated.');
            break;
        }

        return $this->show_page();

    }


    function show_edit_device($device=false){
        global $app;        
        $client = $app->client;
        $device = $device?$device:$this->_get_current_device();

        if(!$device) return $this->show_page(); 

        $vars = array(            
            'error_msg'=>$this->error_msg,
            'ok_msg'=>$this->ok_msg,
            'form_url'=>WebApp::HOME_SUBURL.'&cmd=save_device&device_id='.$device->id,
            'name'=>$device->name
        );

        $html = $this->compile_page('home_edit_device.tmpl',$vars);
        echo $html;

        return true;
    }


     function do_save_device(){
        while(true){
            // check Cancel button
            if( http_post_param("save")=='') break;

            global $app;
            $client = $app->client;
            $device = $this->_get_current_device();
            
            // check valid client id
            if(!$device) break;

            // read submitted data
            $device->name = ltrim(rtrim(http_post_param('name')));
            if($device->name==''){
                $this->error_msg = locstr('Name should be specified.');
                return $this->show_edit_device($device); 
            }

            // save new data
            if(!$client->save_data()){
                $this->error_msg = locstr('Failed to save updated data.');
                return $this->show_edit_device($device);    
            }

            if(!$device->save_name_to_site()){
                $this->error_msg = locstr('Failed to save updated data.');
                return $this->show_edit_device($device);    
            }            

            $this->ok_msg = locstr('Succesfully updated.');
            break;
        }

        return $this->show_page();
    }

    function do_update(){
        global $app;
        $client = $app->client;

        if(!$client->update_from_site()){
            $this->error_msg = locstr('Failed to update data.');
            return false;    
        }

        if(!$client->save_updated()){
            $this->error_msg = locstr('Failed to save updated data.');
            return false;    
        }

        $this->ok_msg = locstr('Succesfully updated.');

        return $this->show_page();

    }

    function do_switch_esm($enable_esm){
        global $app;
        $client = $app->client;

        
        if(!$client->switch_esm($enable_esm)){
            $this->error_msg = locstr('Failed to switch ESM.');
            return false;    
        }

        $this->ok_msg = locstr('Succesfully switched ESM.');

        return $this->show_page();

    }


    function run(){
    	global $app;

        $cmd = http_get_param("cmd");
        log_debug('HomePage: run: cmd="'.$cmd.'"');        
    	
        switch($cmd){
            // =========== COMMON  ====
            case 'update':                
                return $this->do_update();                
            case 'enable_esm':                
            case 'disable_esm':                
                return $this->do_switch_esm($cmd=='enable_esm');                
            // =========== EDIT ZONE  ====
            case 'edit_zone':                
                return $this->show_edit_zone();
            case 'save_zone':                
                return $this->do_save_zone();
            // =========== MANIPULATE ZONE TEMP  ====
            case 'edit_zone_temp':                
                return $this->show_edit_zone_temp();
            case 'save_zone_temp':
                return $this->do_save_zone_temp();
            // =========== DEVICE  ====
            case 'edit_device':                
                return $this->show_edit_device();
            case 'save_device':                
                return $this->do_save_device();
        }

    	return $this->show_page();
    }

    private function _get_current_zone(){
        global $app;
        $zone_id = http_get_param("zone_id");
        $zone =  $zone_id!=''?$app->client->get_zone_by_id($zone_id):false;
        if(!$zone) $this->error_msg = locstr('Failed to find requested zone.');
        return $zone;

    }

    private function _get_current_device(){
        global $app;
        $device_id = http_get_param("device_id");
        $device =  $device_id!=''?$app->client->get_device_by_id($device_id):false;
        if(!$device) $this->error_msg = locstr('Failed to find requested device.');
        return $device;

    }
 }

?>
