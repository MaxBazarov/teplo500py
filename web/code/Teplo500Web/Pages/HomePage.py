from Teplo500.utils import *
from Teplo500Web.web_utils import *
import Teplo500.SalusZone
from Teplo500Web.Pages.AbstractPage import *
import time

class HomePage(AbstractPage):
	
	def __init__(self):
		self.error_msg=''
		self.ok_msg=''

	def show_page(self):
		a = get_app()
		## SHOW DEVICES+ZONES
	
		devices_html = ''
		counter = 0
		esm = False

		for device in a.client.devices:
			zones_html = '';          
			for zone in device.zones:                
				if zone.is_esm():
					esm = true;
				vars = {
					'zone':zone
				}
				zones_html += self.compile_template('home_zone.tmpl',vars)
			
			vars = {
				'device':device,
				'counter':counter,
				'devices_total' : len(a.client.devices),
				'zones_html':zones_html
			}
			devices_html += self.compile_template('home_device.tmpl',vars)
			counter += 1
		
		## SHOW CHARTS
		chart_html = ''
		vars = {
			'date':int(time.time())
		}
		chart_html = self.compile_template('home_chart.tmpl',vars)

		vars = {
			'error_msg' : self.error_msg,
			'ok_msg' : self.ok_msg,
			'home_update_link' : a.urls['HOME_SUBURL']+'&cmd=update',
			'home_switch_esm_link' : a.urls['HOME_SUBURL']+'&cmd='+choose(esm,'disable_esm','enable_esm'),
			'home_switch_esm_text':choose(esm,locstr('Disable Energy Save'),locstr('Enable Energy Save')),
			'updated_raw':a.client.data_updated_time,
			'updated_text' : datetime.fromtimestamp(a.client.data_updated_time).strftime("M d H:i:s"),
			'devices_html':devices_html,
			'chart_html':chart_html,
			'sys_head_custom'  :  self.compile_template('home_head.tmpl',{}),
			'sys_body_custom'  :  ''
		}

		print(self.compile_page('home.tmpl',vars))

		return True


	def show_edit_zone_temp(self,zone=None):
		app = get_app()
		client = app.client

		if zone is None:
			zone = self._get_current_zone()
		if zone is None:
			return self.show_page()


		## define temperature range 
		temps = []
		for x in range(60, 9, -1):
			temps.append(x/2)        
		
		vars = {
			'error_msg' : self.error_msg,
			'ok_msg' : self.ok_msg,
			'temps':temps,
			'form_url' : app.urls['HOME_SUBURL']+'&cmd=save_zone_temp&zone_id='+str(zone.id),
			'man_temp' : zone.current_mode_temp if (zone.mode==Teplo500.SalusZone.MODE_AUTO or zone.mode==Teplo500.SalusZone.MODE_MAN) else zone.current_temp,
			'name':zone.name   
		}

		html = self.compile_page('home_edit_zone_temp.tmpl',vars)
		print(html)

		return True
	
	def do_save_zone_temp(self):
		while(True):
			## check Cancel button
			if http_post_param("save")=='':
				break;

			app = get_app()
			client = app.client;
			zone = self._get_current_zone()
			
			## check valid client id
			if zone is None: 
				break;

			## read submitted data
			new_man_temp = http_post_param('man_temp').lstrip().rstip()
			if new_man_temp=='':
				self.error_msg = locstr('New temperature should be specified.')
				return self.show_edit_zone(zone)
		
			## save new data        
			self.ok_msg = locstr('Succesfully completed.')
			break        

		return self.show_page()


	def show_edit_zone(self,zone=None):
		app = get_app()
		client = app.client
		zone = zone if zone is not None else self._get_current_zone()

		if zone is None:
			return self.show_page()

		vars = {
			'error_msg' : self.error_msg,
			'ok_msg' : self.ok_msg,
			'form_url' : app.urls['HOME_SUBURL']+'&cmd=save_zone&zone_id='+str(zone.id),
			'name':zone.name
		}

		html = self.compile_page('home_edit_zone.tmpl',vars)
		print(html)

		return True


	def do_save_zone(self):
		while(True):
			## check Cancel button
			if http_post_param("save")=='': break

			app = get_app()
			client = app.client
			zone = self._get_current_zone()
			
			## check valid client id
			if zone is None: break

			## read submitted data
			zone.name = http_post_param('name').lstrip().rstrip()
			if zone.name=='':
				self.error_msg = locstr('Name should be specified.')
				return self.show_edit_zone(zone);

			## save new data
			if not client.save_data():
				self.error_msg = locstr('Failed to save updated data.')
				return self.show_edit_zone(zone)

			self.ok_msg = locstr('Succesfully updated.')
			break
		
		return self.show_page()


	def show_edit_device(self,device=None):
		app = get_app()
		client = app.client
		if device is None:
			device =self._get_current_device()

		if device is None:
			return self.show_page();

		vars = {
			'error_msg' : self.error_msg,
			'ok_msg' : self.ok_msg,
			'form_url' : app.urls['HOME_SUBURL']+'&cmd=save_device&device_id='+device.id,
			'name':device.name
		}

		html = self.compile_page('home_edit_device.tmpl',vars)
		print(html)
		return True

	def do_save_device(self):
		while(True):
			## check Cancel button
			if http_post_param("save")=='': break
			
			client = get_app().client;
			device = self._get_current_device()
			
			## check valid client id
			if device is None: break

			## read submitted data
			device.name = http_post_param('name').lstrip().rstrip()
			if device.name=='':
				self.error_msg = locstr('Name should be specified.')
				return self.show_edit_device(device)        

			## save new data
			if not client.save_data():
				self.error_msg = locstr('Failed to save updated data.')
				return self.show_edit_device(device)            

			if not device.save_name_to_site():
				self.error_msg = locstr('Failed to save updated data.')
				return self.show_edit_device(device)
			
			self.ok_msg = locstr('Succesfully updated.')
			break    

		return self.show_page()


	def do_update(self):
		client = get_app().client

		if not client.update_from_site():
			self.error_msg = locstr('Failed to update data.')
			return False
		

		if not client.save_updated():
			self.error_msg = locstr('Failed to save updated data.')
			return False            

		self.ok_msg = locstr('Succesfully updated.')

		return self.show_page()

	def do_switch_esm(self,enable_esm):
		client = get_app().client

		if not client.switch_esm(enable_esm):
			self.error_msg = locstr('Failed to switch ESM.')
			return False        

		self.ok_msg = locstr('Succesfully switched ESM.')

		return self.show_page()


	def run(self):

		cmd = http_get_param("cmd")
		log_debug('HomePage: run: cmd="'+cmd+'"')
				
		## =========== COMMON  ====
		if cmd=='update': 
			return self.do_update()
		if cmd=='enable_esm' or cmd=='disable_esm':
			return self.do_switch_esm(cmd=='enable_esm')
		## =========== EDIT ZONE  ====
		if cmd=='edit_zone':                
			return self.show_edit_zone()
		if cmd=='save_zone':
			return self.do_save_zone()
		## =========== MANIPULATE ZONE TEMP  ====
		if cmd=='edit_zone_temp':                
			return self.show_edit_zone_temp()
		if cmd=='save_zone_temp':
			return self.do_save_zone_temp()
		## =========== DEVICE  ====
		if cmd=='edit_device':
			return self.show_edit_device()
		if cmd=='save_device':                
			return self.do_save_device()        

		return self.show_page()


	def _get_current_zone(self):
		app = get_app()
		zone_id = http_get_param("zone_id")
		zone =  app.client.get_zone_by_id(zone_id) if zone_id!='' else None
		if zone is None:
			 self.error_msg = locstr('Failed to find requested zone.')
		return zone

	def _get_current_device(self):
		app = get_app()
		device_id = http_get_param("device_id")
		device =  app.client.get_device_by_id(device_id) if device_id!='' else None
		if device is None:
			 self.error_msg = locstr('Failed to find requested device.')
		return device
