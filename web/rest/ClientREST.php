<?php

import SalusHistoryHelper

class ClientREST extends AbstractREST
{
	
    function __construct()
    {
         parent::__construct();
    }

    function get_client_data(){
        global $app;

        $date_str = http_get_param('date');
        if($date_str=='') return AbstractREST::ShowNoData(); 
        $date = new DateTime($date_str);

        found = SalusHistoryHelper.find_client_history(app.client,date)
        if($found===false) return AbstractREST::ShowNoData(); 

        raw_data = SalusHistoryHelper.load_client_history(app.client,date)
        if($raw_data===false){
            log_error('ClientREST.get_client_data(): failed to load client history');
            return AbstractREST::ShowError();   
        }

        $colors = array('#FF0000','#00FF00','#0000FF');

        $zone_count = (count($raw_data['header'])-1)/2;
        $labels = array();
        $datasets = array();


        foreach($raw_data['records'] as $record){
            // save time
            $labels[] = $record[0];

            // save zones            
            $zone_index = 0;            
            for($zone_index=0;$zone_index<$zone_count;$zone_index++){          
                // init dataset array
                if(count($datasets)<=$zone_index){
                    array_push($datasets,array(
                        'label'=> strstr( $raw_data['header'][1+$zone_index*2] ,'/',true  ),
                        'backgroundColor' => $colors[$zone_index],
                        'borderColor' => 'window.chartColors.'.$colors[$zone_index],
                        'cubicInterpolationMode' => 'monotone',
                        'data' => array(),
                        'fill' => false
                    ));
                }
                array_push($datasets[$zone_index]['data'],$record[1+$zone_index*2]);
            }
        }

        echo json_encode(array(
            'labels'=>$labels,
            'date'=>date_str($date),
            'date_txt'=>date_txt($date),
            'prev_date'=>date_str($found['prev_date']),        
            'prev_date_txt'=>date_txt($found['prev_date']),
            'next_date'=>date_str($found['next_date']),
            'next_date_txt'=>date_txt($found['next_date']),
            'datasets'=>$datasets
        ),JSON_PRETTY_PRINT);

        return true;
    }

    function run(){
        global $app;    	
        log_debug('SettingsPage: run');
        
        if(http_get_param("cmd")=='get_chart_data'){
            return $this->get_client_data();
        }else{
            return AbstractREST::ShowUknownCmd();   
        }
        
    }
 }

?>
