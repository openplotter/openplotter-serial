#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2019 by e-sailing <https://github.com/e-sailing/openplotter-serial>
#
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import wx, os, webbrowser, subprocess, socket, pyudev, re, ujson, time, configparser
import wx.richtext as rt

from openplotterSettings import conf
from openplotterSettings import language
# use the class "platform" to get info about the host system. See: https://github.com/openplotter/openplotter-settings/blob/master/openplotterSettings/platform.py
from openplotterSettings import platform

class SerialFrame(wx.Frame):
	def __init__(self):
		self.rpitype = ''
		try:
			modelfile = open('/sys/firmware/devicetree/base/model', 'r', 2000)
			self.rpimodel = modelfile.read()[:-1]
			if self.rpimodel == 'Raspberry Pi Zero W Rev 1.1':
				self.rpitype = '0W'
			elif self.rpimodel == 'Raspberry Pi 2 Model B Rev 1.1':
				self.rpitype = '2B'
			elif self.rpimodel == 'Raspberry Pi 3 Model B Rev 1.2':
				self.rpitype = '3B'
			elif self.rpimodel == 'Raspberry Pi 3 Model B Plus Rev 1.3':
				self.rpitype = '3B+'
			elif self.rpimodel == 'Raspberry Pi 4 Model B Rev 1.1':
				self.rpitype = '4B'				
			modelfile.close()
		except:
			self.rpimodel = ''
	
		self.conf = conf.Conf()
		self.conf_folder = self.conf.conf_folder
		self.home = self.conf_folder
		self.home = os.path.expanduser("~")
		self.SK_settings = SK_settings(self.conf)
		self.SK = self.SK_settings.installed
		self.kplex = os.path.exists(self.home +'/.kplex.conf')
		self.gpsd = os.path.exists('/etc/default/gpsd')
		self.pypilot = os.path.exists(self.home+'/pypilot_serial_ports')
		#print(self.SK, self.kplex, self.gpsd, self.pypilot)
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(__file__)
		#self.currentdir = '/home/pi/openplotter-serial/openplotterSerial'
		self.currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-serial',self.currentLanguage)

		wx.Frame.__init__(self, None, title=_('OpenPlotter Serial'), size=(800,444))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		icon = wx.Icon(self.currentdir+"/data/openplotter-serial.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)
		self.CreateStatusBar()
		font_statusBar = self.GetStatusBar().GetFont()
		font_statusBar.SetWeight(wx.BOLD)
		self.GetStatusBar().SetFont(font_statusBar)

		self.toolbar1 = wx.ToolBar(self, style=wx.TB_TEXT)
		toolHelp = self.toolbar1.AddTool(101, _('Help'), wx.Bitmap(self.currentdir+"/data/help.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolHelp, toolHelp)
		if not self.platform.isInstalled('openplotter-doc'): self.toolbar1.EnableTool(101,False)
		toolSettings = self.toolbar1.AddTool(102, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSettings, toolSettings)
		self.toolbar1.AddStretchableSpace()
		self.emptyimage = wx.Bitmap(self.currentdir+"/data/empty.png")
		self.toolbar1.AddTool(105, '', self.emptyimage)
		self.toolbar1.AddTool(106, '', self.emptyimage)

		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.p_serial = wx.Panel(self.notebook)
		self.connections = wx.Panel(self.notebook)
		self.output = wx.Panel(self.notebook)
		self.notebook.AddPage(self.p_serial, _('Name Serial Port (udev)'))
		self.notebook.AddPage(self.connections, _('Jump to SignalK settings or Setup GPIO Serial Port'))
		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/openplotter-24.png", wx.BITMAP_TYPE_PNG))
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/connections.png", wx.BITMAP_TYPE_PNG))
		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)
		self.notebook.SetPageImage(1, img1)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)

		self.pageSerial()
		self.pageConnection()
		
		self.Centre() 

	def ShowStatusBar(self, w_msg, colour):
		self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText(w_msg)

	# red for error or cancellation messages
	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, (130,0,0))

	# green for succesful messages
	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, (0,130,0))

	# black for informative messages
	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK) 

	# yellow for attention messages
	def ShowStatusBarYELLOW(self, w_msg):
		self.ShowStatusBar(w_msg,(255,140,0)) 

	def onTabChange(self, event):
		try:
			self.SetStatusText('')
		except:
			pass

	# create your page in the manuals and add the link here
	def OnToolHelp(self, event): 
		url = "/usr/share/openplotter-doc/template/serial_app.html"
		webbrowser.open(url, new=2)

	def OnToolSettings(self, event): 
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	def OnToolSend(self,e):
		self.notebook.ChangeSelection(0)
		if self.toolbar1.GetToolState(103): self.myoption.SetLabel('1')
		else: self.myoption.SetLabel('0')

	def pageSerial(self):
		self.list_Serialinst = wx.ListCtrl(self.p_serial, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES, size=(-1,200))
		self.list_Serialinst.InsertColumn(0, _('alias')+' /dev/', width=100)
		self.list_Serialinst.InsertColumn(1, _('device')+' /dev/', width=100)
		self.list_Serialinst.InsertColumn(2, _('vendor'), width=60)
		self.list_Serialinst.InsertColumn(3, _('product'), width=60)
		self.list_Serialinst.InsertColumn(4, _('serial'), width=120)
		self.list_Serialinst.InsertColumn(5, _('USB port'), width=120)
		self.list_Serialinst.InsertColumn(6, _('remember'), width=80)
		self.list_Serialinst.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_SerialinstSelected)
		self.list_Serialinst.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_SerialinstDeselected)
		
		ttyOP_label = wx.StaticText(self.p_serial, label='/dev/ttyOP_')
		name_label = wx.StaticText(self.p_serial, label=_('alias'), size=(100,-1))
		self.Serial_OPname = wx.TextCtrl(self.p_serial, size=(100,-1))
	
		dataLabel = wx.StaticText(self.p_serial, label=_('data'), size=(110,-1))
		self.serialData = wx.Choice(self.p_serial, choices=['NMEA 0183','NMEA 2000'], style=wx.CB_READONLY, size=(110,-1))
		self.serialData.Bind(wx.EVT_CHOICE, self.onSelectData)

		assignment_label = wx.StaticText(self.p_serial, label=_('assignment'))
		self.assign0183 = True
		self.assignmentN2K = [_('manual')]
		self.assignment0183 = [_('manual')]
		#self.assignment0183 = [_('manual'),'GPSD','Signal K > OpenCPN','pypilot > Signal K > OpenCPN','GPSD > pypilot > Signal K > OpenCPN']
		self.Serial_assignment = wx.Choice(self.p_serial, choices=self.assignment0183, style=wx.CB_READONLY, size=(100,-1))
		self.Serial_assignment.Bind(wx.EVT_CHOICE, self.onSelectAssigment)

		bauds_label = wx.StaticText(self.p_serial, label=_('bauds'), size=(100,-1))
		self.bauds = ['4800', '9600', '19200', '38400', '57600', '115200', '230400', '460800', '921600']
		self.Serial_baud_select = wx.Choice(self.p_serial, choices=self.bauds, style=wx.CB_READONLY, size=(100,-1))

		self.Serial_rem_dev = wx.RadioButton(self.p_serial, label=_('Remember device (by vendor, product, serial)'))
		self.Serial_rem_port = wx.RadioButton(self.p_serial, label=_('Remember port (positon on the USB-hub)'))

		self.serial_update = wx.Button(self.p_serial, label=_('apply'))
		self.serial_update.Bind(wx.EVT_BUTTON, self.on_update_Serialinst)

		self.serial_delete = wx.Button(self.p_serial, label=_('delete'))
		self.serial_delete.Bind(wx.EVT_BUTTON, self.on_delete_Serialinst)

		refresh = wx.Button(self.p_serial, label=_('refresh'))
		refresh.Bind(wx.EVT_BUTTON, self.read_Serialinst)
		
		row1labels = wx.BoxSizer(wx.HORIZONTAL)
		row1labels.Add((0,0), 0, wx.LEFT | wx.EXPAND, 85)
		row1labels.Add(name_label, 0, wx.LEFT | wx.EXPAND, 5)
		row1labels.Add(dataLabel, 0, wx.LEFT | wx.EXPAND, 5)
		row1labels.Add(assignment_label, 1, wx.LEFT | wx.EXPAND, 5)
		row1labels.Add(bauds_label, 0, wx.LEFT | wx.EXPAND, 5)

		row1 = wx.BoxSizer(wx.HORIZONTAL)
		row1.Add(ttyOP_label, 0, wx.LEFT | wx.UP | wx.EXPAND, 5)
		row1.Add(self.Serial_OPname, 0, wx.LEFT | wx.EXPAND, 5)
		row1.Add(self.serialData, 0, wx.LEFT | wx.EXPAND, 5)
		row1.Add(self.Serial_assignment, 1, wx.LEFT | wx.EXPAND, 5)
		row1.Add(self.Serial_baud_select, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 5)

		col1 = wx.BoxSizer(wx.VERTICAL)
		col1.Add(self.Serial_rem_dev, 0, wx.ALL | wx.EXPAND, 5)
		col1.Add(self.Serial_rem_port, 0, wx.ALL | wx.EXPAND, 5)

		col2 = wx.BoxSizer(wx.HORIZONTAL)
		col2.AddStretchSpacer(1)
		col2.Add(refresh, 0, wx.ALL | wx.EXPAND, 5)
		col2.Add(self.serial_delete, 0, wx.ALL | wx.EXPAND, 5)
		col2.Add(self.serial_update, 0, wx.ALL | wx.EXPAND, 5)

		row2 = wx.BoxSizer(wx.HORIZONTAL)
		row2.Add(col1, 1, wx.ALL | wx.EXPAND, 0)
		row2.Add(col2, 1, wx.ALL | wx.EXPAND, 0)

		v_final = wx.BoxSizer(wx.VERTICAL)
		v_final.Add(self.list_Serialinst, 1, wx.EXPAND, 0)
		v_final.AddSpacer(10)   
		v_final.Add(row1labels, 0, wx.EXPAND, 0)
		v_final.AddSpacer(5)
		v_final.Add(row1, 0, wx.EXPAND, 0)
		v_final.AddSpacer(10)
		v_final.Add(row2, 0, wx.EXPAND, 0)

		self.p_serial.SetSizer(v_final)
				
		self.read_Serialinst()

	def start_udev(self):
		subprocess.call(['sudo', 'udevadm', 'control', '--reload-rules'])
		subprocess.call(['sudo', 'udevadm', 'trigger', '--attr-match=subsystem=tty'])

	def read_Serialinst(self,e=0):	
		self.toolbar1.DeleteTool(105)
		self.toolbar1.DeleteTool(106)
		self.toolbar1.AddTool(105, '', self.emptyimage)
		self.toolbar1.AddTool(106, '', self.emptyimage)

		self.reset_Serial_fields()
		self.ShowStatusBarBLACK('')
		self.list_Serialinst.DeleteAllItems()
		data = self.conf.get('UDEV', 'Serialinst')
		try:
			self.Serialinst = eval(data)
		except:
			self.Serialinst = {}
		self.context = pyudev.Context()

		for device in self.context.list_devices(subsystem='tty'):
			#print(device)
			i = device.get('DEVNAME')
			if not '/dev/moitessier' in i:
				try:
					ii = device.get('DEVLINKS')
				except:
					continue
			if not ('moitessier' in i or 'ttyACM' in i or 'ttyUSB' in i or 'serial0' in i):
				continue
			value = device.get('DEVPATH')
			port = value[value.rfind('/usb1/') + 6:-(len(value) - value.find('/tty'))]
			port = port[port.rfind('/') + 1:]
			try:
				serial = device.get('ID_SERIAL_SHORT')
			except:
				serial = ''
			try:
				vendor_db = device.get('ID_VENDOR_FROM_DATABASE')
			except:
				vendor_db = ''
			try:
				model_db = device.get('ID_MODEL_FROM_DATABASE')
			except:
				model_db = ''
			try:
				vendor_id = device.get('ID_VENDOR_ID')
			except:
				vendor_id = ''
			try:
				model_id = device.get('ID_MODEL_ID')
			except:
				model_id = ''

			# default values if this port is not configured
			name = ''
			assignment = ''
			remember = ''
			bauds = ''
			serialData = ''

			for n in self.Serialinst:
				ii = self.Serialinst[n]

				if ii['remember'] == 'port' and ii['port'] == port:
					if ii['vendor'] != vendor_id or ii['product'] != model_id or str(ii['serial']) != str(serial):
						self.ShowStatusBarRED(_('Device with vendor ') + vendor_id + ' and product ' + model_id + _(' is connected to a reserved port'))
						break
					name = n
					assignment = ii['assignment']
					remember = ii['remember']
					serialData = ii['data']
					try:
						bauds = ii['bauds']
					except: pass
					break
				elif ii['remember'] == 'dev' and ii['vendor'] == vendor_id and ii['product'] == model_id and str(ii['serial']) == str(serial):
					#check if device with same product/vendor/serial has been added
					exist = False
					for i2 in range(self.list_Serialinst.GetItemCount()):
						if n == self.list_Serialinst.GetItemText(i2, 0): exist = True
					if not exist:
						name = n
						assignment = ii['assignment']
						remember = ii['remember']
						serialData = ''
						if 'data' in ii:
							serialData = ii['data']
						try:
							bauds = ii['bauds']
						except: pass

			l = [name, i[5:], vendor_id, model_id, serial, port, remember]
			self.list_Serialinst.Append(l)
			
		for name in self.Serialinst:
			exist = False
			for i in range(self.list_Serialinst.GetItemCount()):
				if name == self.list_Serialinst.GetItemText(i, 0):
					if self.Serialinst[name]['data'] == 'NMEA 0183':
						self.list_Serialinst.SetItemBackgroundColour(i,(102,205,170))
					if self.Serialinst[name]['data'] == 'NMEA 2000':
						self.list_Serialinst.SetItemBackgroundColour(i,(0,191,255))
					exist = True
			if not exist:
				l = [name, self.Serialinst[name]['device'], self.Serialinst[name]['vendor'], self.Serialinst[name]['product'], self.Serialinst[name]['serial'], self.Serialinst[name]['port'], self.Serialinst[name]['remember']]
				self.list_Serialinst.Append(l)
				#self.list_Serialinst.Append([x.decode('utf8') for x in l])
				self.list_Serialinst.SetItemBackgroundColour(self.list_Serialinst.GetItemCount()-1,(255,0,0))
				self.ShowStatusBarRED(_('There are missing devices'))

	def OnSkConnections(self,e):
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/connections/-'
		webbrowser.open(url, new=2)

	def OnSkTo0183(self,e):
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/plugins/sk-to-nmea0183'
		webbrowser.open(url, new=2)

	def OnSkTo2000(self,e):
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/plugins/sk-to-nmea2000'
		webbrowser.open(url, new=2)

	def on_SerialinstSelected(self,e):
		i = e.GetIndex()
		valid = e and i >= 0
		self.reset_Serial_fields()
		if not valid: return

		hublen = 9
		portpos = ''
		usbport = self.list_Serialinst.GetItemText(i, 5)
		#print(self.rpitype,usbport)
		if self.rpitype == '3B':
			if usbport[4:5] == '2': portpos = 'ul'
			elif usbport[4:5] == '4': portpos = 'ur'
			elif usbport[4:5] == '3': portpos = 'll'
			elif usbport[4:5] == '5': portpos = 'lr'
		elif self.rpitype == '3B+':
			if usbport[4:5] == '1':
				hublen = 11
				portpos = 'ul'
				if usbport[6:7] == '3': portpos = 'll'
			elif usbport[4:5] == '2': portpos = 'lr'
			elif usbport[4:5] == '3': portpos = 'ur'
		elif self.rpitype == '4B':
			if usbport[4:5] == '3': portpos = '4ul'
			elif usbport[4:5] == '1': portpos = '4ur'
			elif usbport[4:5] == '4': portpos = '4ll'
			elif usbport[4:5] == '2': portpos = '4lr'

		if portpos != '':
			#print(self.currentdir+"/data/rpi_port_" + portpos + ".png")
			self.toolbar1.DeleteTool(105)
			self.toolbar1.DeleteTool(106)
			
			image = wx.Bitmap(self.currentdir+"/data/rpi_port_" + portpos + ".png")
			self.toolbar1.AddTool(105, 'Raspberry Pi', image)
			
			if len(self.list_Serialinst.GetItemText(i, 5)) > hublen:
				portnr = self.list_Serialinst.GetItemText(i, 5)[hublen-3:hublen]
				if portnr[0:1] in ['1','2','3','4','5','6','7','8']:
					image = wx.Bitmap(self.currentdir+"/data/usbhub.png")
					self.toolbar1.AddTool(106, 'Hub port '+portnr, image)
			else:
				self.toolbar1.AddTool(106, '', self.emptyimage)
				
		name = self.list_Serialinst.GetItemText(i, 0)
		if not name: item = {'data':'','assignment':'','bauds':'','port':self.list_Serialinst.GetItemText(i, 5),'remember':''}
		else: item = self.Serialinst[name]

		self.Serial_OPname.Enable()
		self.serialData.Enable()
		self.Serial_assignment.Enable()
		self.serial_update.Enable()
		self.serial_delete.Enable()
		self.Serial_baud_select.Enable()
		self.Serial_rem_dev.Enable()
		self.Serial_rem_port.Enable()

		self.Serial_OPname.SetValue(name.replace('ttyOP_',''))
		self.serialData.SetStringSelection(item['data'])
		self.onSelectData()
		if item['assignment'] == '0': self.Serial_assignment.SetSelection(0)
		else: self.Serial_assignment.SetStringSelection(item['assignment'])
		self.onSelectAssigment()
		self.Serial_baud_select.SetStringSelection(item['bauds'])
		if 'serial' in item['port'] or 'virtual' in item['port']:
			self.Serial_rem_port.SetValue(True) # remember by port for non usb
			self.Serial_rem_port.Disable()
			self.Serial_rem_dev.SetValue(False)
			self.Serial_rem_dev.Disable()
		else:
			rem = item['remember']
			self.Serial_rem_dev.SetValue(rem == 'dev')
			self.Serial_rem_port.SetValue(rem == 'port')

	def on_delete_Serialinst(self, e):
		index = self.list_Serialinst.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
		if index < 0:
			self.ShowStatusBarYELLOW(_('No device selected'))
			return
		name = self.list_Serialinst.GetItemText(index, 0)
		try:
			del self.Serialinst[name]
		except: return
		self.list_Serialinst.SetItem(index, 0, '')
		self.list_Serialinst.SetItem(index, 6, '')
		self.reset_Serial_fields()
		self.conf.set('UDEV', 'Serialinst', str(self.Serialinst))
		self.apply_changes_Serialinst()

	def on_SerialinstDeselected(self,e):
		self.reset_Serial_fields()
		self.toolbar1.DeleteTool(105)
		self.toolbar1.DeleteTool(106)
		self.toolbar1.AddTool(105, '', self.emptyimage)
		self.toolbar1.AddTool(106, '', self.emptyimage)
		

	def reset_Serial_fields(self):
		self.Serial_OPname.SetValue('')
		self.serialData.SetSelection(-1)
		self.Serial_rem_dev.SetValue(True)
		self.Serial_rem_port.SetValue(False)
		self.Serial_assignment.SetSelection(-1)
		self.Serial_baud_select.SetSelection(-1)
		self.Serial_OPname.Disable()
		self.serialData.Disable()
		self.Serial_assignment.Disable()
		self.serial_update.Disable()
		self.serial_delete.Disable()
		self.Serial_baud_select.Disable()
		self.Serial_rem_dev.Disable()
		self.Serial_rem_port.Disable()
		
	def onSelectData(self, e=0):
		selected = self.serialData.GetStringSelection()
		self.Serial_assignment.Clear()
		self.assign0183 = selected == 'NMEA 0183'
		if self.assign0183: self.Serial_assignment.AppendItems(self.assignment0183)
		else: self.Serial_assignment.AppendItems(self.assignmentN2K)
		self.Serial_baud_select.SetSelection(-1)
		self.Serial_baud_select.Disable()

	def onSelectAssigment(self, e=0):
		self.Serial_baud_select.Disable()
		self.Serial_baud_select.SetSelection(-1)
		selected = self.Serial_assignment.GetStringSelection()
		if selected == 'Signal K > OpenCPN': self.Serial_baud_select.Enable()

	def on_enable_UART(self,e):
		msg = _('This action disables Bluetooth and enables UART. OpenPlotter will reboot.\n')
		msg += _('Are you sure?')
		dlg = wx.MessageDialog(None, msg, _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
		if dlg.ShowModal() == wx.ID_YES: self.edit_boot(True)
		dlg.Destroy()

	def on_disable_UART(self,e):
		msg = _('This action disables UART and enables Bluetooth. OpenPlotter will reboot.\n')
		msg += _('Are you sure?')
		dlg = wx.MessageDialog(None, msg, _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
		if dlg.ShowModal() == wx.ID_YES: self.edit_boot(False)
		dlg.Destroy()

	def edit_boot(self, onoff):
		file = open('/boot/config.txt', 'r')
		file1 = open(self.home+'/config.txt', 'w')
		exists = False
		while True:
			line = file.readline()
			if not line: break
			if onoff and 'dtoverlay=pi3-disable-bt' in line: 
				file1.write('dtoverlay=pi3-disable-bt\n')
				os.system('sudo systemctl disable hciuart')
				exists = True
			elif not onoff and 'dtoverlay=pi3-disable-bt' in line: 
				file1.write('#dtoverlay=pi3-disable-bt\n')
				os.system('sudo systemctl enable hciuart')
				exists = True
			else: file1.write(line)
		if onoff and not exists: 
			file1.write('\ndtoverlay=pi3-disable-bt\n')
			os.system('sudo systemctl disable hciuart')
		file.close()
		file1.close()

		file = open('/boot/cmdline.txt', 'r')
		file1 = open(self.home+'/cmdline.txt', 'w')
		text = file.read()
		text = text.replace('\n', '')
		text_list = text.split(' ')
		if onoff and 'console=serial0,115200' in text_list: 
			text_list.remove('console=serial0,115200')
		if not onoff and not 'console=serial0,115200' in text_list: 
			text_list.append('console=serial0,115200')
		final = ' '.join(text_list)+'\n'
		file1.write(final)
		file.close()
		file1.close()

		reset = False
		if os.system('diff '+self.home+'/config.txt /boot/config.txt > /dev/null'):
			os.system('sudo mv '+self.home+'/config.txt /boot')
			reset = True
		else: os.system('rm -f '+self.home+'/config.txt')
		if os.system('diff '+self.home+'/cmdline.txt /boot/cmdline.txt > /dev/null'):
			os.system('sudo mv '+self.home+'/cmdline.txt /boot')
			reset = True
		else: os.system('rm -f '+self.home+'/cmdline.txt')

		if reset == True : os.system('sudo shutdown -r now')
		
		
	def on_update_Serialinst(self, e=0):

		index = self.list_Serialinst.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
		if index < 0:
			self.ShowStatusBarRED(_('Failed. No port selected'))
			return

		name = self.Serial_OPname.GetValue()
		if not name or not re.match('^[0-9a-z]{1,8}$', name):
			self.ShowStatusBarYELLOW(_('The alias must be a lowercase string between 1 and 8 characters or numbers.'))
			return
		old_name = self.list_Serialinst.GetItemText(index, 0)
		name  = 'ttyOP_'+name
		for i in range(self.list_Serialinst.GetItemCount()):
			if i != index and name == self.list_Serialinst.GetItemText(i, 0):
				self.ShowStatusBarYELLOW(_('Same alias used for multiple devices'))
				return

		data = self.serialData.GetStringSelection()
		if not data:
				self.ShowStatusBarYELLOW(_('Please select type of data'))
				return

		assignmentIndex = self.Serial_assignment.GetSelection()
		if assignmentIndex == -1:
				self.ShowStatusBarYELLOW(_('Please assign the device'))
				return
		elif assignmentIndex == 0:
			assignment = '0'
		else:
			assignment = self.Serial_assignment.GetStringSelection()

		bauds = self.Serial_baud_select.GetStringSelection()
		if assignment == 'Signal K > OpenCPN' and not bauds:
				self.ShowStatusBarYELLOW(_('Please select bauds'))
				return

		if self.Serial_rem_dev.GetValue():
			remember = 'dev'
		else:
			remember = 'port'

		device = self.list_Serialinst.GetItemText(index, 1)
		vendor = self.list_Serialinst.GetItemText(index, 2)
		product = self.list_Serialinst.GetItemText(index, 3)
		serial = self.list_Serialinst.GetItemText(index, 4)
		port = self.list_Serialinst.GetItemText(index, 5)
		ii = {'device':device, 'vendor':vendor, 'product':product, 'port':port, 'serial':serial, 'assignment':assignment, 'remember':remember, 'bauds':bauds,'data':data}

		if old_name and old_name != name: del self.Serialinst[old_name]

		# make sure there are not two ports with the same product/vendor/serial remembered by dev
		for name2 in self.Serialinst:
			if self.Serialinst[name2]['remember'] == 'dev' and ii['remember'] == 'dev' and name != name2:
				if self.Serialinst[name2]['vendor'] == ii['vendor'] and self.Serialinst[name2]['product'] == ii['product'] and self.Serialinst[name2]['serial'] == ii['serial']:
					self.ShowStatusBarYELLOW(_('Device with duplicate vendor and product must be set to "Remember port".'))
					return

		# do not allow entries with the same port and different name
		for name2 in self.Serialinst:
			if self.Serialinst[name2]['remember'] == 'port' and ii['remember'] == 'port' and name != name2:
				if self.Serialinst[name2]['port'] == ii['port']:
					self.ShowStatusBarYELLOW(_('This port is already reserved and must be set to "Remember device".'))
					return
		
		self.Serialinst[name] = ii
		self.conf.set('UDEV', 'Serialinst', str(self.Serialinst))		
		
		self.apply_changes_Serialinst()
										
	def apply_changes_Serialinst(self):
		filename = self.home +'/10-openplotter.rules'
		if not os.path.isfile(filename):
			file = open(filename, 'w+')
		else:
			file = open(filename, 'w')
		for name in self.Serialinst:
			i = self.Serialinst[name]
			if 'virtual' == i['port']:
				write_str = 'KERNEL=="'+i['device']
			elif 'port' == i['remember']: # non-usb serial
				write_str = 'KERNEL=="' + i['device'] + '*", KERNELS=="' + i['port']
			else:
				write_str = 'SUBSYSTEM=="tty", ATTRS{idVendor}=="' + i['vendor']
				write_str += '",ATTRS{idProduct}=="' + i['product']
				if i['serial'] != '' and i['serial'] != 'None':
					write_str += '",ATTRS{serial}=="' + i['serial']
			name = name.replace('/dev/','')
			write_str += '",SYMLINK+="' + name + '"\n'
			file.write(write_str)
		file.close()
		test = 0
		test = os.system('sudo mv '+self.home +'/10-openplotter.rules /etc/udev/rules.d')

		self.ShowStatusBarYELLOW(_('Applying changes ...'))
		self.start_udev()

		# write gpsd config
		if self.gpsd:
			gpsd_exists = False
			file = open('/etc/default/gpsd', 'r')
			file1 = open(self.home+'/gpsd', 'w')
			while True:
				line = file.readline()
				if not line: break
				if line[:9] == 'DEVICES="':
					file1.write('DEVICES="')
					for name in self.Serialinst:
						if self.Serialinst[name]['assignment'] == 'GPSD' or self.Serialinst[name]['assignment'] == 'GPSD > pypilot > Signal K > OpenCPN':
							gpsd_exists = True
							file1.write(name + ' ')
					file1.write('"\n')
				else: file1.write(line)
			file.close()
			file1.close()

			if os.system('diff '+self.home+'/gpsd /etc/default/gpsd > /dev/null'):
				os.system('sudo mv '+self.home+'/gpsd /etc/default')
				os.system('sudo service gpsd restart')
			else: os.system('rm -f '+self.home+'/gpsd')

		# write pypilot allowed ports
		if self.pypilot:
			resetPypilot = False
			file = open(self.home+'/pypilot_serial_ports', 'w')
			for name in self.Serialinst:
				if self.Serialinst[name]['assignment'] == 'pypilot > Signal K > OpenCPN':
					file.write(name + '\n')
			file.close()
			path = self.home + '/.pypilot/serial_ports'
			if os.system('diff '+self.home+'/pypilot_serial_ports ' + path + ' > /dev/null'):
				os.system('mv '+self.home+'/pypilot_serial_ports ' + path)
				resetPypilot = True
			else: os.system('rm -f '+self.home+'/pypilot_serial_ports')

			checkPypilot = False
			pypilotMode = self.conf.get('PYPILOT', 'mode')
			for name in self.Serialinst:
				if 'pypilot' in self.Serialinst[name]['assignment']: checkPypilot = True
			if checkPypilot:
				if pypilotMode != 'basic autopilot':
					self.conf.set('PYPILOT', 'mode', 'basic autopilot')
					resetPypilot = True
			else:
				if pypilotMode == 'basic autopilot':
					check_imu = self.check_imu()
					if check_imu: 
						imu_data = eval(check_imu) 
						imu_name = imu_data[0][0]
						if imu_name != '0': 
							self.conf.set('PYPILOT', 'mode', 'imu')
							resetPypilot = True
						else: 
							self.conf.set('PYPILOT', 'mode', 'disabled')
							resetPypilot = True
					else: 
						self.conf.set('PYPILOT', 'mode', 'disabled')
						resetPypilot = True

			if resetPypilot:
				self.read_pypilot()
				self.on_apply_changes_pypilot()

		# check kplex interfaces
		if self.kplex:
			kplexfile = open(self.home +'/.kplex.conf', 'r', 2000)
			data = kplexfile.read()
			kplexfile.close()
			#split in kplex blocks
			datas = data.split('[')
			datanew = ''
			for ikplex in datas:
				if ikplex.split(']')[0] == 'serial':
					exists = False
					for alias in self.Serialinst:
						if alias in ikplex and self.Serialinst[alias]['data'] == 'NMEA 0183' and self.Serialinst[alias]['assignment'] == '0': exists = True
					#if one of the serial settings is equal -> it should stay
					if exists:
						datanew += '['+ikplex
					#if one there is no serial everything should be deleted except comments
					elif '###' in ikplex:
						datanew += ikplex[ikplex.find('###'):]
				else:
					datanew += '['+ikplex

			#on changes write new conf and restart kplex
			if datas != datanew:
				try:
					kplexfile = open(self.home +'/.kplex.conf', 'w', 2000)
				except:pass
				else:
					kplexfile.write(datanew[1:])
					kplexfile.close()
					msg = _('Restarting kplex... ')
					seconds = 5
					subprocess.call(['pkill', '-f', 'diagnostic-NMEA.py'])
					subprocess.call(['pkill', '-f', 'kplex.py'])
					subprocess.call(['pkill', '-15', 'kplex'])
					for i in range(seconds, 0, -1):
						self.ShowStatusBarYELLOW(msg+str(i))
						time.sleep(1)
					subprocess.Popen('kplex')
					self.ShowStatusBarGREEN(_('Kplex restarted'))
			
		# check SK devices
		if self.SK:
			if self.SK_settings.setSKsettings(): self.restart_SK(0)
			else: time.sleep(1)

		self.read_Serialinst()
		#self.read_n2k()

		# check connections
		exists = False
		for alias in self.Serialinst:
			if self.Serialinst[alias]['data'] == 'NMEA 2000' and self.Serialinst[alias]['assignment'] == 'Signal K > OpenCPN':
				exists = True
		if exists:
			wx.MessageBox(_('You have assigned one or more N2K devices to Signal K > OpenCPN.\n\nThey are ready to send data to Signal K but if you want OpenCPN to get data from Signal K you need to use the Signal K plugins "SK to NMEA 0183" and "N2K AIS to NMEA0183".\n\nYour devices are also ready to send data from Signal K to your N2K network. Use the Signal K plugin "SK to N2K" and allow PGNs transmission using the "Open TX PGNs" tool.\n\n Go to "CAN" tab to access plugins and settings.'), 'Warning', wx.OK | wx.ICON_WARNING)

		checkOpencpn = False
		for alias in self.Serialinst:
			assignment = self.Serialinst[alias]['assignment'] 
			if 'OpenCPN' in assignment: checkOpencpn = True
		if checkOpencpn:
			Osettings = opencpnSettings()
			opencpnConnection = Osettings.getConnectionState()
			if not opencpnConnection:
				wx.MessageBox(_('The default OpenCPN connection is missing and it is not getting data from Signal K. Please create this connection in OpenCPN:\n\nNetwork\nProtocol: TCP\nAddress: localhost\nData Port: 10110'), 'Warning', wx.OK | wx.ICON_WARNING)
			elif opencpnConnection == 'disabled': 
				wx.MessageBox(_('The default OpenCPN connection is disabled and it is not getting data from Signal K. Please enable this connection in OpenCPN:\n\nNetwork\nProtocol: TCP\nAddress: localhost\nData Port: 10110'), 'Warning', wx.OK | wx.ICON_WARNING)

	def OnRemoveButton(self, e):
		index = self.list_Serialinst.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
		if index < 0:
			self.ShowStatusBarYELLOW(_('No device selected'))
			return
		name = self.list_Serialinst.GetItemText(index, 0)
		try:
			del self.Serialinst[name]
		except: return
		self.list_Serialinst.SetItem(index, 0, '')
		self.list_Serialinst.SetItem(index, 6, '')
		self.reset_Serial_fields()
		self.conf.set('UDEV', 'Serialinst', str(self.Serialinst))
		self.apply_changes_Serialinst()
		

	def pageConnection(self):
		self.toolbar3 = wx.ToolBar(self.connections, style=wx.TB_TEXT)
		skConnections = self.toolbar3.AddTool(302, _('SK Connection'), wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.OnSkConnections, skConnections)
		self.toolbar3.AddSeparator()
		skTo0183 = self.toolbar3.AddTool(303, 'SK → NMEA 0183', wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.OnSkTo0183, skTo0183)
		skTo2000 = self.toolbar3.AddTool(304, 'SK → NMEA 2000', wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.OnSkTo2000, skTo2000)

		enableUART = wx.Button(self.connections, label=_('enable UART'))
		enableUART.Bind(wx.EVT_BUTTON, self.on_enable_UART)

		disableUART = wx.Button(self.connections, label=_('disable UART'))
		disableUART.Bind(wx.EVT_BUTTON, self.on_disable_UART)
		
		self.SK_activ = wx.CheckBox(self.connections, label=_('setup serial port in Signal K (not recommended)'))
		self.SK_activ.Bind(wx.EVT_CHECKBOX, self.on_SK_activ)

		self.gpsd_activ = wx.CheckBox(self.connections, label=_('setup serial port in gpsd (not recommended)'))
		self.gpsd_activ.Bind(wx.EVT_CHECKBOX, self.on_gpsd_activ)

		self.pypilot_activ = wx.CheckBox(self.connections, label=_('setup serial port in pypilot (not recommended)'))
		self.pypilot_activ.Bind(wx.EVT_CHECKBOX, self.on_pypilot_activ)

		row2 = wx.BoxSizer(wx.HORIZONTAL)
		row2.AddStretchSpacer(1)
		row2.Add(enableUART, 0, wx.ALL | wx.EXPAND, 5)
		row2.Add(disableUART, 0, wx.ALL | wx.EXPAND, 5)
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar3, 0, wx.LEFT | wx.EXPAND, 0)
		vbox.Add(row2, 0, wx.LEFT | wx.EXPAND, 0)
		vbox.Add(self.SK_activ, 0, wx.LEFT | wx.EXPAND, 0)
		vbox.Add(self.gpsd_activ, 0, wx.LEFT | wx.EXPAND, 0)
		vbox.Add(self.pypilot_activ, 0, wx.LEFT | wx.EXPAND, 0)
		vbox.AddStretchSpacer(1)
		self.connections.SetSizer(vbox)	
		self.printConnections()
		
	def printConnections(self):
		# Check if Signal K and some plugins are installed
		if self.platform.skPort: 
			self.toolbar3.EnableTool(302,True)
			self.toolbar3.EnableTool(303,True)
			if self.platform.isSKpluginInstalled('signalk-to-nmea2000'):
				self.toolbar3.EnableTool(304,True)
			else: self.toolbar3.EnableTool(304,False)
		else:
			self.toolbar3.EnableTool(302,False)
			self.toolbar3.EnableTool(303,False)
			self.toolbar3.EnableTool(304,False)
		
	def on_SK_activ(self, e):
		if self.SK_activ.GetValue():
			if not ('Signal K > OpenCPN' in self.assignment0183):
				self.assignment0183.append('Signal K > OpenCPN')
				self.assignmentN2K.append('Signal K > OpenCPN')

				self.Serial_assignment.Clear()
				if self.assign0183: self.Serial_assignment.AppendItems(self.assignment0183)
				else: self.Serial_assignment.AppendItems(self.assignmentN2K)
		else:
			if 'Signal K > OpenCPN' in self.assignment0183:
				self.assignment0183.remove('Signal K > OpenCPN')
				self.assignmentN2K.remove('Signal K > OpenCPN')
				
				self.Serial_assignment.Clear()
				if self.assign0183: self.Serial_assignment.AppendItems(self.assignment0183)
				else: self.Serial_assignment.AppendItems(self.assignmentN2K)
	
	def on_gpsd_activ(self, e):
		if self.gpsd_activ.GetValue():
			if not ('GPSD' in self.assignment0183):
				self.assignment0183.append('GPSD')

				self.Serial_assignment.Clear()
				if self.assign0183: self.Serial_assignment.AppendItems(self.assignment0183)
		else:
			if 'GPSD' in self.assignment0183:
				self.assignment0183.remove('GPSD')

				self.Serial_assignment.Clear()
				if self.assign0183: self.Serial_assignment.AppendItems(self.assignment0183)

	def on_pypilot_activ(self, e):
		if self.pypilot_activ.GetValue():
			if not ('pypilot > Signal K > OpenCPN' in self.assignment0183):
				self.assignment0183.append('pypilot > Signal K > OpenCPN')
				if self.gpsd_activ.GetValue(): self.assignment0183.append('GPSD > pypilot > Signal K > OpenCPN')

				self.Serial_assignment.Clear()
				if self.assign0183: self.Serial_assignment.AppendItems(self.assignment0183)
		else:
			if 'pypilot > Signal K > OpenCPN' in self.assignment0183:
				self.assignment0183.remove('pypilot > Signal K > OpenCPN')
				if 'GPSD > pypilot > Signal K > OpenCPN' in self.assignment0183:
					self.assignment0183.remove('GPSD > pypilot > Signal K > OpenCPN')

				self.Serial_assignment.Clear()
				if self.assign0183: self.Serial_assignment.AppendItems(self.assignment0183)

################################################################################

	def start_SK(self):
		subprocess.call(['sudo', 'systemctl', 'start', 'signalk.socket'])
		subprocess.call(['sudo', 'systemctl', 'start', 'signalk.service'])

	def stop_SK(self):
		subprocess.call(['sudo', 'systemctl', 'stop', 'signalk.service'])
		subprocess.call(['sudo', 'systemctl', 'stop', 'signalk.socket'])
		
	def restart_SK(self, msg):
		if msg == 0: msg = _('Restarting Signal K server... ')
		seconds = 12
		self.stop_SK()
		self.start_SK()
		for i in range(seconds, 0, -1):
			self.ShowStatusBarYELLOW(msg+str(i))
			time.sleep(1)
		self.ShowStatusBarGREEN(_('Signal K server restarted'))
		
################################################################################
		
class opencpnSettings:

	def __init__(self):

		home = os.path.expanduser("~")
		self.confFile = home+'/.opencpn/opencpn.conf'
		self.installed_openocpn = os.path.exists(self.confFile)			

		if self.installed_openocpn:
			self.confData = configparser.ConfigParser()

	def getConnectionState(self):
		if self.installed_openocpn:
			result = False
			self.confData.read(self.confFile)
			tmp = self.confData.get('Settings/NMEADataSource', 'DataConnections')
			connections = tmp.split('|')
			for connection in connections:
				#0;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18
				#serial/network;TCP/UDP/GPSD;address;port;?;serialport;bauds;?;0=input/1=input+output/2=output;?;?;?;?;?;?;?;?;enabled/disabled;comments
				items = connection.split(';')
				if items[0] == '1':
					if items[1] == '0':
						if items[2] == 'localhost':
							if items[3] == '10110':
								if items[8] == '0' or items[8] == '1':
									if items[17] == '1': result = 'enabled'
									else: result = 'disabled'
			return result
		return True

################################################################################

class SK_settings:

	def __init__(self, conf):
		self.installed = False
		self.conf = conf
		self.home = os.path.expanduser("~")
		self.setting_file = self.home+'/.signalk/settings.json'
		self.load()

	def load(self):
		if os.path.exists(self.setting_file):
			with open(self.setting_file) as data_file:
				self.data = ujson.load(data_file)
			self.installed = True			
		else:
			self.data = {}

	def setSKsettings(self):
		write = False
		serialInst = self.conf.get('UDEV', 'Serialinst')
		try: serialInst = eval(serialInst)
		except: serialInst = {}
		#serial NMEA 0183 devices
		for alias in serialInst:
			if serialInst[alias]['data'] == 'NMEA 0183' and serialInst[alias]['assignment'] == 'Signal K > OpenCPN':
				exists = False
				if 'pipedProviders' in self.data:
					count = 0
					for i in self.data['pipedProviders']:
						if i['id'] == alias:
							exists = True
							if i['pipeElements'][0]['options']['subOptions']['baudrate'] != int(serialInst[alias]['bauds']):
								write = True
								self.data['pipedProviders'][count]['pipeElements'][0]['options']['subOptions']['baudrate'] = int(serialInst[alias]['bauds'])
						count = count + 1
				if not exists:
					self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': 'NMEA0183', 'subOptions': {"validateChecksum": True, "type": "serial", "device": '/dev/'+alias, "baudrate": int(serialInst[alias]['bauds'])}}}], 'enabled': True, 'id': alias})
					write = True
		count = 0
		for i in self.data['pipedProviders']:
			if 'ttyOP_' in i['id'] and i['pipeElements'][0]['options']['subOptions']['type'] == 'serial':
				exists = False
				for alias in serialInst:
					if alias == i['id'] and serialInst[alias]['data'] == 'NMEA 0183' and serialInst[alias]['assignment'] == 'Signal K > OpenCPN':
						exists = True
				if not exists:
					write = True
					del self.data['pipedProviders'][count]
			count = count + 1
		#serial NMEA 2000 devices
		for alias in serialInst:
			if serialInst[alias]['data'] == 'NMEA 2000' and serialInst[alias]['assignment'] == 'Signal K > OpenCPN':
				exists = False
				if 'pipedProviders' in self.data:
					count = 0
					for i in self.data['pipedProviders']:
						if i['id'] == alias:
							exists = True
							if i['pipeElements'][0]['options']['subOptions']['baudrate'] != int(serialInst[alias]['bauds']):
								write = True
								self.data['pipedProviders'][count]['pipeElements'][0]['options']['subOptions']['baudrate'] = int(serialInst[alias]['bauds'])
						count = count + 1
				if not exists:
					self.data['pipedProviders'].append({'pipeElements': [{'type': 'providers/simple', 'options': {'logging': False, 'type': 'NMEA2000', 'subOptions': {'device': '/dev/'+alias, "baudrate": int(serialInst[alias]['bauds']), 'type': 'ngt-1-canboatjs'}}}], 'enabled': True, 'id': alias})
					write = True
		count = 0
		for i in self.data['pipedProviders']:
			if 'ttyOP_' in i['id'] and i['pipeElements'][0]['options']['subOptions']['type'] == 'ngt-1-canboatjs':
				exists = False
				for alias in serialInst:
					if alias == i['id'] and serialInst[alias]['data'] == 'NMEA 2000' and serialInst[alias]['assignment'] == 'Signal K > OpenCPN':
						exists = True
				if not exists:
					write = True
					del self.data['pipedProviders'][count]
			count = count + 1

		if write: self.write_settings()
		return write

	def write_settings(self):
		data = ujson.dumps(self.data, indent=4, sort_keys=True)
		try:
			wififile = open(self.setting_file, 'w')
			wififile.write(data.replace('\/','/'))
			wififile.close()
			self.load()
		except: print('Error: error saving Signal K settings')

################################################################################

def main():
	app = wx.App()
	SerialFrame().Show()
	app.MainLoop()

if __name__ == '__main__':
	main()
