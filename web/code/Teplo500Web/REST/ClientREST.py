import time
from datetime import date
from datetime import datetime
import json

from Teplo500.utils import *

from Teplo500.SalusHistoryHelper import *
from Teplo500Web.REST.AbstractREST import *

class ClientREST(AbstractREST):

    def get_client_data(self):
        app = get_app()

        date_str = http_get_param('date')
        if date_str=='': 
            return self.ShowNoData()
        date = datetime.strptime(date_str,Constants.datetime)

        found = SalusHistoryHelper.find_client_history(app.client,date)
        if not found:
             return self.ShowNoData()

        raw_data = SalusHistoryHelper.load_client_history(app.client,date)
        if raw_data is None:
            log_error('ClientREST.get_client_data(): failed to load client history')
            return self.ShowError()    

        colors = ['#FF0000','#00FF00','#0000FF']

        zone_count = (len(raw_data['header'])-1)/2
        labels = []
        datasets = []

        for record in raw_data['records']:
            ## save time
            labels.append(record[0])

            ## save zones            
            zone_index = 0
            for zone_index in range(0,zone_count-1):
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

        print(json.dumps({
            'labels':labels,
            'date':date_str(date),
            'date_txt':date_txt(date),
            'prev_date':date_str(found['prev_date']),        
            'prev_date_txt':date_txt(found['prev_date']),
            'next_date':date_str(found['next_date']),
            'next_date_txt':date_txt(found['next_date']),
            'datasets':datasets
        }))

        return True


    def run(self):
        app = get_app()    	
        log_debug('SettingsPage: run')
        
        if http_get_param("cmd")=='get_chart_data':
            return self.get_client_data()
        else:
            return self.ShowUknownCmd()
        