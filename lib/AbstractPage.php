<?php

class AbstractPage
{
   function __construct()
	{			
	
	}

	function run(){

	}


	function compile_template($file_name,$variables)
    {
        global $app;

        // extend variables
        $variables['sys_name'] = 'Teplo 500';
        
        if($app->client) $variables['sys_client_name'] = $app->client->name;
        $variables['sys_baseurl'] = $app->base_url();
        $variables['sys_home_link'] = WebApp::HOME_SUBURL;
        $variables['sys_settings_link'] = WebApp::SETTINGS_SUBURL;
        $variables['sys_account_link'] = WebApp::ACCOUNT_SUBURL;
        $variables['sys_logout_link'] = WebApp::LOGOUT_SUBURL;


        $path_to_file = $app->web_path().'/Templates/'.$file_name;

         if(!file_exists($path_to_file))
         {
             log_error('AbstractPage: Template File not found: '.$path_to_file);
             return false;
         }         

        ob_start();

        extract($variables);
        include $path_to_file;

        $html = ob_get_contents();
        ob_end_clean();

        return $html;
    }

    function compile_page($file_name,$variables)
    {
        global $app;
      
        // prep navigation
        $variables['menu_'.$app->page().'_active'] = 'active';
        $variables['layout_top'] = $this->compile_template('layout_top.tmpl',$variables);
        $variables['layout_bottom'] = $this->compile_template('layout_bottom.tmpl',$variables);

        return $this->compile_template($file_name,$variables);
    }


}
?>
