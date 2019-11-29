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

import wx, os, webbrowser, subprocess, pyudev, re, ujson, sys
import wx.richtext as rt
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform

class SerialFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.home = self.conf.home
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(__file__)
		self.currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-serial',self.currentLanguage)
		if self.platform.isRPI:
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
			except: self.rpimodel = ''
	
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
		self.toolbar1.AddSeparator()
		uart = self.toolbar1.AddCheckTool(103, _('UART'), wx.Bitmap(self.currentdir+"/data/uart.png"))
		self.Bind(wx.EVT_TOOL, self.onUart, uart)
		try:
			subprocess.check_output(['systemctl', 'is-active', 'hciuart']).decode(sys.stdin.encoding)
			self.toolbar1.ToggleTool(103,False)
		except: self.toolbar1.ToggleTool(103,True)
		self.toolbar1.AddSeparator()
		refresh = self.toolbar1.AddTool(104, _('Refresh'), wx.Bitmap(self.currentdir+"/data/refresh.png"))
		self.Bind(wx.EVT_TOOL, self.read_Serialinst, refresh)

		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.p_serial = wx.Panel(self.notebook)
		self.connections = wx.Panel(self.notebook)
		self.notebook.AddPage(self.p_serial, _('Devices'))
		self.notebook.AddPage(self.connections, _('Connections'))
		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/usb.png", wx.BITMAP_TYPE_PNG))
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
		
		maxi = self.conf.get('GENERAL', 'maximize')
		if maxi == '1': self.Maximize()

		self.Centre() 

	def ShowStatusBar(self, w_msg, colour):
		self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText(w_msg)

	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, (130,0,0))

	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, (0,130,0))

	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK) 

	def ShowStatusBarYELLOW(self, w_msg):
		self.ShowStatusBar(w_msg,(255,140,0)) 

	def onTabChange(self, event):
		try:
			self.SetStatusText('')
		except: pass

	def OnToolHelp(self, event): 
		url = "/usr/share/openplotter-doc/serial/serial_app.html"
		webbrowser.open(url, new=2)

	def OnToolSettings(self, event): 
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	def pageSerial(self):
		self.imgPorts = wx.ImageList(24, 24)
		self.imgPorts.Add(wx.Bitmap(self.currentdir+"/data/rpi_port_ll.png", wx.BITMAP_TYPE_PNG))
		self.imgPorts.Add(wx.Bitmap(self.currentdir+"/data/rpi_port_lr.png", wx.BITMAP_TYPE_PNG))
		self.imgPorts.Add(wx.Bitmap(self.currentdir+"/data/rpi_port_ul.png", wx.BITMAP_TYPE_PNG))
		self.imgPorts.Add(wx.Bitmap(self.currentdir+"/data/rpi_port_ur.png", wx.BITMAP_TYPE_PNG))
		self.imgPorts.Add(wx.Bitmap(self.currentdir+"/data/rpi_port_4ll.png", wx.BITMAP_TYPE_PNG))
		self.imgPorts.Add(wx.Bitmap(self.currentdir+"/data/rpi_port_4lr.png", wx.BITMAP_TYPE_PNG))
		self.imgPorts.Add(wx.Bitmap(self.currentdir+"/data/rpi_port_4ul.png", wx.BITMAP_TYPE_PNG))
		self.imgPorts.Add(wx.Bitmap(self.currentdir+"/data/rpi_port_4ur.png", wx.BITMAP_TYPE_PNG))
		if self.platform.isRPI:
			colImages = 130
			colSerial = 90
		else:
			colImages = 30
			colSerial = 190
		self.list_Serialinst = wx.ListCtrl(self.p_serial, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES, size=(-1,200))
		self.list_Serialinst.InsertColumn(0, ' ', width=colImages)
		self.list_Serialinst.InsertColumn(1, _('USB port'), width=80)
		self.list_Serialinst.InsertColumn(2, _('device')+' /dev/', width=90)
		self.list_Serialinst.InsertColumn(3, _('alias')+' /dev/', width=100)
		self.list_Serialinst.InsertColumn(4, _('vendor'), width=60)
		self.list_Serialinst.InsertColumn(5, _('product'), width=60)
		self.list_Serialinst.InsertColumn(6, _('serial'), width=colSerial)
		self.list_Serialinst.InsertColumn(7, _('remember'), width=80)
		self.list_Serialinst.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_SerialinstSelected)
		self.list_Serialinst.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_SerialinstDeselected)
		self.list_Serialinst.SetImageList(self.imgPorts, wx.IMAGE_LIST_SMALL)
		
		ttyOP_label = wx.StaticText(self.p_serial, label='/dev/ttyOP_')
		name_label = wx.StaticText(self.p_serial, label=_('alias'), size=(100,-1))
		self.Serial_OPname = wx.TextCtrl(self.p_serial, size=(100,-1))
	
		dataLabel = wx.StaticText(self.p_serial, label=_('data'), size=(110,-1))
		self.serialData = wx.Choice(self.p_serial, choices=['NMEA 0183','NMEA 2000'], style=wx.CB_READONLY, size=(110,-1))

		self.Serial_rem_dev = wx.RadioButton(self.p_serial, label=_('Remember device (by vendor, product, serial)'))
		self.Serial_rem_port = wx.RadioButton(self.p_serial, label=_('Remember port (positon on the USB-hub)'))

		self.toolbar2 = wx.ToolBar(self.p_serial, style=wx.TB_TEXT | wx.TB_VERTICAL)
		self.serial_update = self.toolbar2.AddTool(201, _('Apply'), wx.Bitmap(self.currentdir+"/data/apply.png"))
		self.Bind(wx.EVT_TOOL, self.on_update_Serialinst, self.serial_update)
		self.serial_delete = self.toolbar2.AddTool(202, _('Delete'), wx.Bitmap(self.currentdir+"/data/cancel.png"))
		self.Bind(wx.EVT_TOOL, self.on_delete_Serialinst, self.serial_delete)

		row1labels = wx.BoxSizer(wx.HORIZONTAL)
		row1labels.Add((0,0), 0, wx.LEFT | wx.EXPAND, 85)
		row1labels.Add(name_label, 0, wx.LEFT | wx.EXPAND, 5)
		row1labels.Add(dataLabel, 0, wx.LEFT | wx.EXPAND, 5)

		row1 = wx.BoxSizer(wx.HORIZONTAL)
		row1.Add(ttyOP_label, 0, wx.LEFT | wx.UP | wx.EXPAND, 5)
		row1.Add(self.Serial_OPname, 0, wx.LEFT | wx.EXPAND, 5)
		row1.Add(self.serialData, 0, wx.LEFT | wx.EXPAND, 5)

		col1 = wx.BoxSizer(wx.VERTICAL)
		col1.Add(self.list_Serialinst, 1, wx.ALL | wx.EXPAND, 5)
		col1.Add(row1labels, 0, wx.ALL | wx.EXPAND, 5)
		col1.Add(row1, 0, wx.ALL | wx.EXPAND, 5)
		col1.Add(self.Serial_rem_dev, 0, wx.ALL | wx.EXPAND, 5)
		col1.Add(self.Serial_rem_port, 0, wx.ALL | wx.EXPAND, 5)

		v_final = wx.BoxSizer(wx.HORIZONTAL)
		v_final.Add(col1, 1, wx.EXPAND, 0)
		v_final.Add(self.toolbar2, 0, wx.EXPAND, 0)

		self.p_serial.SetSizer(v_final)
				
		self.read_Serialinst()

	def start_udev(self):
		subprocess.call(['sudo', 'udevadm', 'control', '--reload-rules'])
		subprocess.call(['sudo', 'udevadm', 'trigger', '--attr-match=subsystem=tty'])

	def read_Serialinst(self,e=0):	
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
			#print (device)
			i = device.get('DEVNAME')
			if not '/dev/moitessier' in i:
				try:
					ii = device.get('DEVLINKS')
				except:
					continue
			if not ('moitessier' in i or 'ttyACM' in i or 'ttyUSB' in i or 'serial0' in i or 'ttyS0' in i):
				continue
			value = device.get('DEVPATH')
			port = value[value.rfind('/usb1/') + 6:-(len(value) - value.find('/tty'))]
			port = port[port.rfind('/') + 1:]
			serial = ''
			vendor_id = ''
			model_id = ''
			for tag in device:
				print (tag+': '+device.get(tag))
				if tag == 'ID_SERIAL': serial = device.get('ID_SERIAL')
				if tag == 'ID_SERIAL_SHORT': serial = device.get('ID_SERIAL_SHORT')
				if tag == 'ID_VENDOR_FROM_DATABASE': vendor_id = device.get('ID_VENDOR_FROM_DATABASE')
				if tag == 'ID_VENDOR_ID': vendor_id = device.get('ID_VENDOR_ID')
				if tag == 'ID_MODEL_FROM_DATABASE': model_id = device.get('ID_MODEL_FROM_DATABASE')
				if tag == 'ID_MODEL_ID': model_id = device.get('ID_MODEL_ID')
			# default values if this port is not configured
			name = ''
			remember = ''
			serialData = ''

			for n in self.Serialinst:
				ii = self.Serialinst[n]

				if ii['remember'] == 'port' and ii['port'] == port:
					if ii['vendor'] != vendor_id or ii['product'] != model_id or str(ii['serial']) != str(serial):
						self.ShowStatusBarRED(_('Device with vendor ') + vendor_id + ' and product ' + model_id + _(' is connected to a reserved port'))
						break
					name = n
					remember = ii['remember']
					serialData = ii['data']
					break
				elif ii['remember'] == 'dev' and ii['vendor'] == vendor_id and ii['product'] == model_id and str(ii['serial']) == str(serial):
					#check if device with same product/vendor/serial has been added
					exist = False
					for i2 in range(self.list_Serialinst.GetItemCount()):
						if n == self.list_Serialinst.GetItemText(i2, 3): exist = True
					if not exist:
						name = n
						remember = ii['remember']
						serialData = ''
						if 'data' in ii:
							serialData = ii['data']

			l = [port, i[5:], name, vendor_id, model_id, serial, remember]

			#select image
			if self.platform.isRPI:
				'''
				0 /data/rpi_port_ll.png
				1 /data/rpi_port_lr.png
				2 /data/rpi_port_ul.png
				3 /data/rpi_port_ur.png
				4 /data/rpi_port_4ll.png
				5 /data/rpi_port_4lr.png
				6 /data/rpi_port_4ul.png
				7 /data/rpi_port_4ur.png
				'''
				hublen = 9
				portpos = ''
				usbport = l[0]
				hubtext = ''
				image = ''
				if self.rpitype == '3B':
					if usbport[4:5] == '2': portpos = 2
					elif usbport[4:5] == '4': portpos = 3
					elif usbport[4:5] == '3': portpos = 0
					elif usbport[4:5] == '5': portpos = 1
				elif self.rpitype == '3B+':
					if usbport[4:5] == '1':
						hublen = 11
						portpos = 2
						if usbport[6:7] == '3': portpos = 0
					elif usbport[4:5] == '2': portpos = 1
					elif usbport[4:5] == '3': portpos = 3
				elif self.rpitype == '4B':
					if usbport[4:5] == '3': portpos = 6
					elif usbport[4:5] == '1': portpos = 7
					elif usbport[4:5] == '4': portpos = 4
					elif usbport[4:5] == '2': portpos = 5
				
				if len(usbport) > hublen:
					portnr = usbport[hublen-3:hublen]
					if portnr[0:1] in ['1','2','3','4','5','6','7','8']:
						hubtext = 'Hub port '+portnr
				if portpos: item = self.list_Serialinst.InsertItem(self.list_Serialinst.GetItemCount(), hubtext, portpos)
				else: item = self.list_Serialinst.InsertItem(0, ' ')
			else:
				item = self.list_Serialinst.InsertItem(0, str(self.list_Serialinst.GetItemCount()+1))
			if l[0]: self.list_Serialinst.SetItem(item, 1, l[0])
			if l[1]: self.list_Serialinst.SetItem(item, 2, l[1])
			if l[2]: self.list_Serialinst.SetItem(item, 3, l[2])
			if l[3]: self.list_Serialinst.SetItem(item, 4, l[3])
			if l[4]: self.list_Serialinst.SetItem(item, 5, l[4])
			if l[5]: self.list_Serialinst.SetItem(item, 6, l[5])
			if l[6]: self.list_Serialinst.SetItem(item, 7, l[6])
			
		for name in self.Serialinst:
			exist = False
			for iii in range(self.list_Serialinst.GetItemCount()):
				if name == self.list_Serialinst.GetItemText(iii, 3):
					if self.Serialinst[name]['data'] == 'NMEA 0183':
						self.list_Serialinst.SetItemBackgroundColour(iii,(102,205,170))
					if self.Serialinst[name]['data'] == 'NMEA 2000':
						self.list_Serialinst.SetItemBackgroundColour(iii,(0,191,255))
					exist = True
			if not exist:
				l = ['', self.Serialinst[name]['port'], self.Serialinst[name]['device'], name, self.Serialinst[name]['vendor'], self.Serialinst[name]['product'], self.Serialinst[name]['serial'], self.Serialinst[name]['remember']]
				self.list_Serialinst.Append(l)
				self.list_Serialinst.SetItemBackgroundColour(self.list_Serialinst.GetItemCount()-1,(255,0,0))
				self.ShowStatusBarRED(_('There are missing devices'))

	def OnSkConnections(self,e):
		url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/connections/-'
		webbrowser.open(url, new=2)

	def on_SerialinstSelected(self,e):
		i = e.GetIndex()
		valid = e and i >= 0
		self.reset_Serial_fields()
		if not valid: return
				
		name = self.list_Serialinst.GetItemText(i, 3)
		if not name: item = {'data':'','port':self.list_Serialinst.GetItemText(i, 1),'remember':''}
		else: item = self.Serialinst[name]

		self.Serial_OPname.Enable()
		self.serialData.Enable()
		self.Serial_rem_dev.Enable()
		self.Serial_rem_port.Enable()

		self.Serial_OPname.SetValue(name.replace('ttyOP_',''))
		self.serialData.SetStringSelection(item['data'])

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
		name = self.list_Serialinst.GetItemText(index, 3)
		try:
			del self.Serialinst[name]
		except: return
		self.list_Serialinst.SetItem(index, 3, '')
		self.list_Serialinst.SetItem(index, 7, '')
		self.reset_Serial_fields()
		self.conf.set('UDEV', 'Serialinst', str(self.Serialinst))
		self.apply_changes_Serialinst()

	def on_SerialinstDeselected(self,e):
		self.reset_Serial_fields()
		
	def reset_Serial_fields(self):
		self.Serial_OPname.SetValue('')
		self.serialData.SetSelection(-1)
		self.Serial_rem_dev.SetValue(True)
		self.Serial_rem_port.SetValue(False)
		self.Serial_OPname.Disable()
		self.serialData.Disable()
		self.Serial_rem_dev.Disable()
		self.Serial_rem_port.Disable()

	def onUart(self,e):
		if self.toolbar1.GetToolState(103):
			msg = _('This action disables Bluetooth and enables UART interface in GPIO. OpenPlotter will reboot.\n')
			msg += _('Are you sure?')
			dlg = wx.MessageDialog(None, msg, _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
			if dlg.ShowModal() == wx.ID_YES: self.edit_boot(True)
		else:
			msg = _('This action disables UART interface in GPIO and enables Bluetooth. OpenPlotter will reboot.\n')
			msg += _('Are you sure?')
			dlg = wx.MessageDialog(None, msg, _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
			if dlg.ShowModal() == wx.ID_YES: self.edit_boot(False)
		try:
			subprocess.check_output(['systemctl', 'is-active', 'hciuart']).decode(sys.stdin.encoding)
			self.toolbar1.ToggleTool(103,False)
		except: self.toolbar1.ToggleTool(103,True)
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
		old_name = self.list_Serialinst.GetItemText(index, 3)
		name  = 'ttyOP_'+name
		for i in range(self.list_Serialinst.GetItemCount()):
			if i != index and name == self.list_Serialinst.GetItemText(i, 3):
				self.ShowStatusBarYELLOW(_('Same alias used for multiple devices'))
				return

		data = self.serialData.GetStringSelection()
		if not data:
				self.ShowStatusBarYELLOW(_('Please select type of data'))
				return

		if self.Serial_rem_dev.GetValue():
			remember = 'dev'
		else:
			remember = 'port'

		device = self.list_Serialinst.GetItemText(index, 2)
		vendor = self.list_Serialinst.GetItemText(index, 4)
		product = self.list_Serialinst.GetItemText(index, 5)
		serial = self.list_Serialinst.GetItemText(index, 6)
		port = self.list_Serialinst.GetItemText(index, 1)
		ii = {'device':device, 'vendor':vendor, 'product':product, 'port':port, 'serial':serial, 'remember':remember,'data':data}

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

		self.read_Serialinst()

		'''
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

		'''

	def OnRemoveButton(self, e):
		index = self.list_Serialinst.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
		if index < 0:
			self.ShowStatusBarYELLOW(_('No device selected'))
			return
		name = self.list_Serialinst.GetItemText(index, 3)
		try:
			del self.Serialinst[name]
		except: return
		self.list_Serialinst.SetItem(index, 3, '')
		self.list_Serialinst.SetItem(index, 7, '')
		self.reset_Serial_fields()
		self.conf.set('UDEV', 'Serialinst', str(self.Serialinst))
		self.apply_changes_Serialinst()	

	def pageConnection(self):
		self.toolbar3 = wx.ToolBar(self.connections, style=wx.TB_TEXT)
		skConnections = self.toolbar3.AddTool(302, _('SK Connection'), wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.OnSkConnections, skConnections)
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar3, 0, wx.LEFT | wx.EXPAND, 0)
		vbox.AddStretchSpacer(1)

		self.connections.SetSizer(vbox)	

################################################################################

def main():
	app = wx.App()
	SerialFrame().Show()
	app.MainLoop()

if __name__ == '__main__':
	main()
