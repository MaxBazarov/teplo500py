<?php

class AbstractREST
{
   	function __construct()
	{			
		global $app;
	
	}

	function run(){
    }

    static function show_non_auth_error(){
    	echo '401';

    	return false;
    }

	static function ShowUknownCmd()
	{
		global $app;		
		http_response_code(404);
		
		return false;
	}

	static function ShowNoData()
	{
		global $app;		
		http_response_code(404);
		return false;
	}

	static function ShowError()
	{
		global $app;		
		echo '403';
		return false;
	}
}
?>
