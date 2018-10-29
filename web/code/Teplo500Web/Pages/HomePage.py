from teplo500.core import *
from Teplo500Web.web_core import *
import teplo500.SalusZone
import teplo500.core as core
from Teplo500Web.Pages.abstract_page import *


import time

def home_page_register(flask):
	flask.add_url_rule('/', 'homepage_index', homepage_index)
	flask.add_url_rule('/home', 'homepage_index', homepage_index)
	flask.add_url_rule('/home/devices/<device_id>/edit', 'homepage_edit_device', homepage_edit_device)
	flask.add_url_rule('/home/devices/<device_id>/save', 'homepage_save_device', homepage_save_device,methods=['POST'])
	flask.add_url_rule('/home/zones/<zone_id>/edit', 'homepage_edit_zone', homepage_edit_zone)
	flask.add_url_rule('/home/zones/<zone_id>/save', 'homepage_save_zone', homepage_save_zone,methods=['POST'])
	
	flask.add_url_rule('/home/update', 'homepage_update', homepage_update)
	flask.add_url_rule('/home/esm/enable', 'homepage_enable_esm', homepage_enable_esm)
	flask.add_url_rule('/home/esm/disable', 'homepage_disable_esm', homepage_disable_esm)
	return True

def homepage_index():
	page = HomePage()
	return core.app.create_response(page.show_index())
	
def homepage_edit_device(device_id):
	page = HomePage()	
	page.device_id = device_id

	return core.app.create_response( page.show_edit_device())

def homepage_save_device(device_id):
	page = HomePage()
	page.device_id = device_id

	html = page.do_save_device()
	return core.app.create_response( html )

def homepage_edit_zone(zone_id):
	page = HomePage()	
	page.zone_id = zone_id

	return core.app.create_response( page.show_edit_zone())

def homepage_save_zone(zone_id):
	page = HomePage()
	page.zone_id = zone_id

	html = page.do_save_zone()
	return core.app.create_response( html )

def homepage_update():
	page = HomePage()
	return core.app.create_response( page.do_update())


def homepage_enable_esm():
	page = HomePage()
	return core.app.create_response( page.do_switch_esm(True))

def homepage_disable_esm():
	page = HomePage()
	return core.app.create_response( page.do_switch_esm(False))


class HomePage(AbstractPage):
		
	def __init__(self):
		super().__init__()
		self.error_msg=''
		self.ok_msg=''		

	def show_index(self):
		## SHOW DEVICES+ZONES
	
		devices_html = ''
		counter = 0
		esm = False

		
		for device in core.app.client.devices:
			zones_html = ''          
			for zone in device.zones:                
				if zone.is_esm():
					esm = True
				vars = {
					'zone':zone
				}
				zones_html += self.compile_template('home_zone.tmpl',vars)
			
			vars = {
				'device':device,
				'counter':counter,
				'devices_total' : len(core.app.client.devices),
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
			'home_update_link' : core.app.urls['HOME_SUBURL']+'/update',
			'home_switch_esm_link' : core.app.urls['HOME_SUBURL']+'/esm/'+('disable' if esm else 'enable'),
			'home_switch_esm_text':choose(esm,locstr('Disable Energy Save'),locstr('Enable Energy Save')),
			'updated_raw':core.app.client.data_updated_time,
			'updated_text' : datetime.fromtimestamp(core.app.client.data_updated_time).strftime("M d H:i:s"),
			'devices_html':devices_html,
			'chart_html':chart_html,
			'sys_head_custom'  :  self.compile_template('home_head.tmpl',{}),
			'sys_body_custom'  :  ''
		}

		return self.compile_page('home.tmpl',vars)


	def show_edit_zone_temp(self,zone=None):
		client = core.app.client

		if zone is None:
			zone = self._get_current_zone()
		if zone is None:
			return self.show_index()


		## define temperature range 
		temps = []
		for x in range(60, 9, -1):
			temps.append(x/2)        
		
		vars = {
			'error_msg' : self.error_msg,
			'ok_msg' : self.ok_msg,
			'temps':temps,
			'form_url' : core.app.urls['HOME_SUBURL']+'/zones/'+str(zone.id)+"/save_temp",
			'man_temp' : zone.current_mode_temp if (zone.mode==teplo500.SalusZone.MODE_AUTO or zone.mode==teplo500.SalusZone.MODE_MAN) else zone.current_temp,
			'name':zone.name   
		}

		html = self.compile_page('home_edit_zone_temp.tmpl',vars)
		print(html)

		return True
	
	def do_save_zone_temp(self):
		while(True):
			## check Cancel button
			if http_post_param("save")=='':
				break

			client = core.app.client
			zone = self._get_current_zone()
			
			## check valid client id
			if zone is None: 
				break

			## read submitted data
			new_man_temp = http_post_param('man_temp').lstrip().rstip()
			if new_man_temp=='':
				self.error_msg = locstr('New temperature should be specified.')
				return self.show_edit_zone(zone)
		
			## save new data        
			self.ok_msg = locstr('Succesfully completed.')
			break        

		return self.show_index()


	def show_edit_zone(self,zone=None):
		client = core.app.client
		zone = zone if zone!=None else self._get_current_zone()		

		if not zone:
			return self.show_index()

		vars = {
			'error_msg' : self.error_msg,
			'ok_msg' : self.ok_msg,
			'form_url' : core.app.urls['HOME_SUBURL']+'/zones/'+str(zone.id)+"/save",
			'name':zone.name
		}

		html = self.compile_page('home_edit_zone.tmpl',vars)
		return html


	def do_save_zone(self):
		while(True):
			## check Cancel button
			if http_post_param("save")=='': break

			client = core.app.client
			zone = self._get_current_zone()
			
			## check valid client id
			if zone is None: break

			## read submitted data
			zone.name = http_post_param('name').lstrip().rstrip()
			if zone.name=='':
				self.error_msg = locstr('Name should be specified.')
				return self.show_edit_zone(zone)

			## save new data
			if not client.save_data():
				self.error_msg = locstr('Failed to save updated data.')
				return self.show_edit_zone(zone)

			self.ok_msg = locstr('Succesfully updated.')
			break
		
		return self.show_index()


	def show_edit_device(self,device=None):
		client = core.app.client
		if device is None:
			device =self._get_current_device()

		if device is None:
			return self.show_index()	

		vars = {
			'error_msg' : self.error_msg,
			'ok_msg' : self.ok_msg,
			'form_url' : core.app.urls['HOME_SUBURL']+'/devices/'+device.id + "/save",
			'name':device.name
		}

		html = self.compile_page('home_edit_device.tmpl',vars)
		return html

	def do_save_device(self):
		while(True):
			## check Cancel button
			if http_post_param("save")=='': break
			
			client = core.app.client
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

		return self.show_index()


	def do_update(self):
		client = core.app.client

		if not client.update_from_site():
			self.error_msg = locstr('Failed to update data.')
			return self.show_index()
		

		if not client.save_updated():
			self.error_msg = locstr('Failed to save updated data.')
			return self.show_index()            

		self.ok_msg = locstr('Succesfully updated.')

		return self.show_index()

	def do_switch_esm(self,enable_esm):
		client = core.app.client

		if not client.switch_esm(enable_esm):
			self.error_msg = locstr('Failed to switch ESM.')
			return False        

		self.ok_msg = locstr('Succesfully switched ESM.')

		return self.show_index()

		
	def run(self,cmd):
				
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

		return self.show_index()


	def _get_current_zone(self):		
		zone_id = self.zone_id
		zone =  core.app.client.get_zone_by_id(zone_id) if zone_id!='' else None
		if zone is None:
			 self.error_msg = locstr('Failed to find requested zone.')
		return zone

	def _get_current_device(self):
		device_id = self.device_id
		device =  core.app.client.get_device_by_id(device_id) if device_id!='' else None
		if device is None:
			 self.error_msg = locstr('Failed to find requested device.')
		return device
