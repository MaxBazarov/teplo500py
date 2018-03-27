<?php
class EmailTemplate
{
    const TEMPLATES_FOLDER = '/system/email_templates';
    const EMAILS_FOLDER = '/local/logs/emails';

    var $variables = array();
    var $path_to_file= array();
    var $template_name = '';

    function __construct($template_name)
    {
        $this->template_name = $template_name;
    }

    public function __set($key,$val)
    {
        $this->variables[$key] = $val;
    }


    private function _compile($file_name_postfix)
    {
        global $app;
        $path_to_file = $app->home_path().EmailTemplate::TEMPLATES_FOLDER.'/'.$this->template_name.$file_name_postfix.'.'.$app->lang;

         if(!file_exists($path_to_file))
         {
             log_error('EmailTemplate: Template File not found: '.$path_to_file);
             return false;
         }

        ob_start();

        extract($this->variables);
        include $path_to_file;

        $content = ob_get_contents();
        ob_end_clean();

        return $content;
    }

    function compile_body()
    {
        return $this->_compile('_body');
    }

     function compile_subject()
    {
        return $this->_compile('_subject');
    }

}

class Emailer
{
    var $recipients = array();
    var $template;
    var $template_subject;

    public function __construct($to = false)
    {
        if($to !== false)
        {
            if(is_array($to))
            {
                foreach($to as $_to){ $this->recipients[$_to] = $_to; }
            }else
            {
                $this->recipients[$to] = $to; //1 Recip
            }
        }
    }

    function set_template( $template)
    {

        $this->template = $template;
    }

    function send() 
    {        
        global $app;

        $subject = $this->template->compile_subject();
        $body = $this->template->compile_body();

        // SEND REAL EMAIL USING GMAIL
        $gmail = $app->config->gmail;
        if($gmail->enabled){
            ///
            require_once '../lib/vendor/swiftmailer/swiftmailer/lib/swift_required.php';

            $transport = Swift_SmtpTransport::newInstance('smtp.gmail.com', 465, "ssl")
              ->setUsername($gmail->auth_name)
              ->setPassword($gmail->auth_key);

            $mailer = Swift_Mailer::newInstance($transport);

            $message = Swift_Message::newInstance($subject)
              ->setFrom(array('mbazarov@gmail.com' => 'Mailer'))
              ->setTo($this->recipients)
              ->setBody( $body );

            $result = $mailer->send($message);
            if($result===false)
            {
                log_error('Emailer: send : failed');
                return false;
            }
            log_ok('Emailer: send : sent ok');
    
        }

        // DUMP EMAIL INFO FILE
        {

        }

        
        return true;

    }
}
?>