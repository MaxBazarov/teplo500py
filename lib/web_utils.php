<?php


function http_post_param($name)
{
	if(!array_key_exists($name,$_POST)) return '';
	return htmlspecialchars($_POST[$name]);
}


function http_get_param($name)
{
	if(!array_key_exists($name,$_GET)) return '';
	return htmlspecialchars($_GET[$name]);
}




?>