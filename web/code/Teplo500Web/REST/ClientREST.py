import time
from datetime import date
from datetime import datetime
import json

from Teplo500.core import *
from Teplo500.core import Constants

import Teplo500.SalusHistoryHelper
from Teplo500Web.REST.AbstractREST import *


def rest_register(flask):
	flask.add_url_rule('/rest/get_chart_data/<sdate>', 'rest_client_get_data', rest_client_get_data)
	return True

def rest_client_get_data(sdate):
	rest = ClientREST()
	return get_app().create_response(rest.get_client_data(sdate))

class ClientREST(AbstractREST):

    def get_client_data(self,sdate):
        app = get_app()

        if app.client_id=='':
            return self.show_non_auth_error()

        if sdate=='': 
            return self.ShowNoData()
        odate = str_date(sdate)

        found = Teplo500.SalusHistoryHelper.find_client_history(app.client,odate)
        if not found:
            log_debug('ClientREST.get_client_data(): find_client_history failed')
            return self.ShowNoData()

        raw_data = Teplo500.SalusHistoryHelper.load_client_history(app.client,odate)
        if raw_data is None:
            log_error('ClientREST.get_client_data(): failed to load client history')
            return self.ShowError()    

        colors = ['#FF0000','#00FF00','#0000FF']

        zone_count = int((len(raw_data['header'])-1)/2)
        labels = []
        datasets = []

        log_debug("ClientREST.get_client_data(): zone_count="+str(zone_count))

        for record in raw_data['records']:
            ## save time
            labels.append(record[0])

            ## save zones            
            zone_index = 0
            log_debug("ClientREST.get_client_data(): header="+record[0])
            for zone_index in range(0,zone_count):
                log_debug('ClientREST.get_client_data(): process zone:'+str(zone_index))
                ## init dataset array
                if len(datasets)<=zone_index:
                    datasets.append({
                        'label': raw_data['header'][1+zone_index*2].split('/')[0],
                        'backgroundColor' : colors[zone_index],
                        'borderColor' : 'window.chartColors.'+colors[zone_index],
                        'cubicInterpolationMode' : 'monotone',
                        'data' : [],
                        'fill' : False
                    })                
                datasets[zone_index]['data'].append(record[1+zone_index*2])                 

        return json.dumps({
            'labels':labels,
            'date':day_str(odate),
            'day_txt':day_txt(odate),
            'prev_date':day_str(found['prev_date']),        
            'prev_day_txt':day_txt(found['prev_date']),
            'next_date':day_str(found['next_date']),
            'next_day_txt':day_txt(found['next_date']),
            'datasets':datasets
        })
