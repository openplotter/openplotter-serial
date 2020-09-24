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

import wx, os, webbrowser, subprocess, re, ujson, sys, time
import wx.richtext as rt
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from openplotterSettings import selectConnections
from openplotterSettings import serialPorts
if os.path.dirname(os.path.abspath(__file__))[0:4] == '/usr':
	from .version import version
else:
	import version

class SerialFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.home = self.conf.home
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
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
	
		wx.Frame.__init__(self, None, title=_('Serial')+' '+version, size=(800,444))
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
		if not self.platform.isRPI: self.toolbar1.EnableTool(103,False)
		try:
			subprocess.check_output(['systemctl', 'is-active', 'hciuart']).decode(sys.stdin.encoding)
			self.toolbar1.ToggleTool(103,False)
		except: self.toolbar1.ToggleTool(103,True)
		self.toolbar1.AddSeparator()
		refresh = self.toolbar1.AddTool(104, _('Refresh'), wx.Bitmap(self.currentdir+"/data/refresh.png"))
		self.Bind(wx.EVT_TOOL, self.onToolRefresh, refresh)

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
		self.read_Serialinst()

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

	def OnToolSettings(self, event=0): 
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	def onToolRefresh(self,e):
		self.ShowStatusBarBLACK('')
		self.read_Serialinst()

	##########################################################################

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
			colSerial = 75
		else:
			colImages = 30
			colSerial = 175
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
		self.list_Serialinst.SetTextColour(wx.BLACK)

		ttyOP_label = wx.StaticText(self.p_serial, label='/dev/ttyOP_')
		name_label = wx.StaticText(self.p_serial, label=_('alias'), size=(100,-1))
		self.Serial_OPname = wx.TextCtrl(self.p_serial, size=(100,-1))
	
		dataLabel = wx.StaticText(self.p_serial, label=_('data'), size=(110,-1))
		self.serialData = wx.Choice(self.p_serial, choices=['NMEA 0183','NMEA 2000', 'Signal K'], style=wx.CB_READONLY, size=(110,-1))

		self.Serial_rem_dev = wx.RadioButton(self.p_serial, label=_('Remember device (by vendor, product, serial)'))
		self.Serial_rem_port = wx.RadioButton(self.p_serial, label=_('Remember port (positon on the USB-hub)'))

		self.toolbar2 = wx.ToolBar(self.p_serial, style=wx.TB_TEXT | wx.TB_VERTICAL)
		self.serial_update = self.toolbar2.AddTool(201, _('Apply'), wx.Bitmap(self.currentdir+"/data/apply.png"))
		self.Bind(wx.EVT_TOOL, self.on_update_Serialinst, self.serial_update)
		self.serial_delete = self.toolbar2.AddTool(202, _('Remove'), wx.Bitmap(self.currentdir+"/data/cancel.png"))
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

	def read_Serialinst(self,e=0):	
		self.reset_Serial_fields()
		self.onListConnectionsDeselected()
		self.list_Serialinst.DeleteAllItems()
		self.listConnections.DeleteAllItems()

		data = self.conf.get('UDEV', 'Serialinst')
		try:
			self.Serialinst = eval(data)
		except:
			self.Serialinst = {}

		serialDevices = selectConnections.Serial()
		for device in serialDevices.devices:
			devname = device.get('DEVNAME')
			value = device.get('DEVPATH')
			port = value[value.rfind('/usb1/') + 6:-(len(value) - value.find('/tty'))]
			port = port[port.rfind('/') + 1:]
			serial = ''
			if devname[8:10] == 'SC': serial = devname[10:11]
			vendor_id = ''
			model_id = ''
			for tag in device:
				if tag == 'ID_SERIAL_SHORT': serial = device.get('ID_SERIAL_SHORT')
				if tag == 'ID_VENDOR_ID': vendor_id = device.get('ID_VENDOR_ID')
				if tag == 'ID_MODEL_ID': model_id = device.get('ID_MODEL_ID')
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

			l = [port, devname[5:], name, vendor_id, model_id, serial, remember]
			l2 = [devname[5:], name]

			if devname[8:10] == 'SC':
				l[5] = devname[10:11]
				hubtext = ''
				if l[5] == '2': hubtext = _('upper left') 
				elif l[5] == '5': hubtext = _('upper right') 
				elif l[5] == '1': hubtext = _('middle left') 
				elif l[5] == '4': hubtext = _('middle right') 
				elif l[5] == '0': hubtext = _('lower left') 
				elif l[5] == '3': hubtext = _('lower right') 
				item = self.list_Serialinst.InsertItem(self.list_Serialinst.GetItemCount(), hubtext)
			else:
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
					hubtext = _('no Hub')
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
					if portpos != '' and not 'virtual' in usbport and not 'serial' in usbport: 
						item = self.list_Serialinst.InsertItem(self.list_Serialinst.GetItemCount(), hubtext, portpos)
					else: 
						item = self.list_Serialinst.InsertItem(self.list_Serialinst.GetItemCount(), ' ')
				else:
					item = self.list_Serialinst.InsertItem(self.list_Serialinst.GetItemCount(), str(self.list_Serialinst.GetItemCount()+1))
			if l[0]: self.list_Serialinst.SetItem(item, 1, l[0])
			if l[1]: self.list_Serialinst.SetItem(item, 2, l[1])
			if l[2]: self.list_Serialinst.SetItem(item, 3, l[2])
			if l[3]: self.list_Serialinst.SetItem(item, 4, l[3])
			if l[4]: self.list_Serialinst.SetItem(item, 5, l[4])
			if l[5]: self.list_Serialinst.SetItem(item, 6, l[5])
			if l[6]: self.list_Serialinst.SetItem(item, 7, l[6])

			if l2[1]:
				item = self.listConnections.InsertItem(self.listConnections.GetItemCount(), l2[0])
				self.listConnections.SetItem(item, 1, l2[1])
			
		for name in self.Serialinst:
			for iii in range(self.listConnections.GetItemCount()):
				if name in self.listConnections.GetItemText(iii, 1):
					if self.Serialinst[name]['data']: 
						self.listConnections.SetItem(iii, 2, self.Serialinst[name]['data'])

			exist = False
			for iii in range(self.list_Serialinst.GetItemCount()):
				if name == self.list_Serialinst.GetItemText(iii, 3):
					if self.Serialinst[name]['data'] == 'NMEA 0183':
						self.list_Serialinst.SetItemBackgroundColour(iii,(102,205,170))
					if self.Serialinst[name]['data'] == 'NMEA 2000':
						self.list_Serialinst.SetItemBackgroundColour(iii,(0,191,255))
					if self.Serialinst[name]['data'] == 'Signal K':
						self.list_Serialinst.SetItemBackgroundColour(iii,(255,215,0))
					exist = True
			#check missing devices
			if not exist:
				l = ['', self.Serialinst[name]['port'], self.Serialinst[name]['device'], name, self.Serialinst[name]['vendor'], self.Serialinst[name]['product'], self.Serialinst[name]['serial'], self.Serialinst[name]['remember']]
				self.list_Serialinst.Append(l)
				self.list_Serialinst.SetItemBackgroundColour(self.list_Serialinst.GetItemCount()-1,(255,0,0))
				self.ShowStatusBarRED(_('There are missing devices'))

		# check existing connections
		allSerialPorts = serialPorts.SerialPorts()
		usedSerialPorts = allSerialPorts.getSerialUsedPorts()
		for i in usedSerialPorts:
			exists = False
			for ii in range(self.listConnections.GetItemCount()):
				if i['device'] == '/dev/'+self.listConnections.GetItemText(ii, 1):
					if not self.listConnections.GetItemText(ii, 3):
						if i['data'] == self.listConnections.GetItemText(ii, 2).replace(' ',''):
							exists = True
							self.listConnections.SetItem(ii, 3, i['app'])
							self.listConnections.SetItem(ii, 4, i['id'])
							self.listConnections.SetItem(ii, 5, str(i['baudrate']))
			if not exists:
				if 'ttyOP_' in i['device']:
					item = self.listConnections.InsertItem(self.listConnections.GetItemCount(), '')
					self.listConnections.SetItem(item, 1, i['device'].replace('/dev/',''))
				else:
					item = self.listConnections.InsertItem(self.listConnections.GetItemCount(), i['device'].replace('/dev/',''))
				data = ''
				if i['data'] == 'NMEA0183': data = 'NMEA 0183'
				if i['data'] == 'NMEA2000': data = 'NMEA 2000'
				if i['data'] == 'SignalK': data = 'Signal K'
				self.listConnections.SetItem(item, 2, data)
				self.listConnections.SetItem(item, 3, i['app'])
				self.listConnections.SetItem(item, 4, i['id'])
				self.listConnections.SetItem(item, 5, str(i['baudrate']))


		#setting colours
		for i in range(self.listConnections.GetItemCount()):
			enabled = False
			for iii in usedSerialPorts:
				if iii['app'] == self.listConnections.GetItemText(i, 3) and iii['id'] == self.listConnections.GetItemText(i, 4): enabled = iii['enabled']
			if enabled:
				if self.listConnections.GetItemText(i, 0) and self.listConnections.GetItemText(i, 1) and self.listConnections.GetItemText(i, 3):
					if self.listConnections.GetItemText(i, 2) == 'NMEA 0183':
						self.listConnections.SetItemBackgroundColour(i,(102,205,170))
					elif self.listConnections.GetItemText(i, 2) == 'NMEA 2000':
						self.listConnections.SetItemBackgroundColour(i,(0,191,255))
					elif self.listConnections.GetItemText(i, 2) == 'Signal K':
						self.listConnections.SetItemBackgroundColour(i,(255,215,0))
			for ii in range(self.listConnections.GetItemCount()):
				if not self.listConnections.GetItemText(ii, 0) and self.listConnections.GetItemText(ii, 1):
					self.listConnections.SetItemBackgroundColour(ii,(255,0,0))
				else:
					enabled2 = False
					for iii in usedSerialPorts:
						if iii['app'] == self.listConnections.GetItemText(ii, 3) and iii['id'] == self.listConnections.GetItemText(ii, 4): enabled2 = iii['enabled']
					if self.listConnections.GetItemText(i, 0) == self.listConnections.GetItemText(ii, 0) and i != ii and enabled and enabled2:
						self.listConnections.SetItemBackgroundColour(i,(255,0,0))
						self.listConnections.SetItemBackgroundColour(ii,(255,0,0))
					if self.listConnections.GetItemText(i, 1) == self.listConnections.GetItemText(ii, 1) and i != ii and enabled and enabled2:
						self.listConnections.SetItemBackgroundColour(i,(255,0,0))
						self.listConnections.SetItemBackgroundColour(ii,(255,0,0))

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

	def on_SerialinstSelected(self,e):
		i = e.GetIndex()
		valid = e and i >= 0
		self.reset_Serial_fields()
		if not valid: return

		self.toolbar2.EnableTool(201,True)
		name = self.list_Serialinst.GetItemText(i, 3)
		if not name: 
			item = {'data':'','port':self.list_Serialinst.GetItemText(i, 1),'remember':''}
			self.toolbar2.EnableTool(202,False)
		else: 
			item = self.Serialinst[name]
			self.toolbar2.EnableTool(202,True)

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
		self.toolbar2.EnableTool(201,False)
		self.toolbar2.EnableTool(202,False)

	def onUart(self,e):
		if self.toolbar1.GetToolState(103):
			msg = _('This action disables Bluetooth and enables UART interface in GPIO. OpenPlotter will reboot.\n')
			msg += _('Are you sure?')
			dlg = wx.MessageDialog(None, msg, _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
			if dlg.ShowModal() == wx.ID_YES: 
				subprocess.call([self.platform.admin, 'python3', self.currentdir+'/service.py', 'uartTrue'])
		else:
			msg = _('This action disables UART interface in GPIO and enables Bluetooth. OpenPlotter will reboot.\n')
			msg += _('Are you sure?')
			dlg = wx.MessageDialog(None, msg, _('Question'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
			if dlg.ShowModal() == wx.ID_YES: 
				subprocess.call([self.platform.admin, 'python3', self.currentdir+'/service.py', 'uartFalse'])
		try:
			subprocess.check_output(['systemctl', 'is-active', 'hciuart']).decode(sys.stdin.encoding)
			self.toolbar1.ToggleTool(103,False)
		except: self.toolbar1.ToggleTool(103,True)
		dlg.Destroy()
		
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
		self.ShowStatusBarYELLOW(_('Applying changes ...'))
		filename = self.home +'/10-openplotter.rules'
		if not os.path.isfile(filename):
			file = open(filename, 'w+')
		else:
			file = open(filename, 'w')
		for name in self.Serialinst:
			i = self.Serialinst[name]
			if 'virtual' == i['port'] or 'SC' == i['device'][3:5]:
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
		subprocess.call([self.platform.admin, 'python3', self.currentdir+'/service.py', 'udev', self.home+'/10-openplotter.rules'])
		self.read_Serialinst()
		self.ShowStatusBarGREEN(_('Applied changes'))

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

	##########################################################################

	def pageConnection(self):
		self.toolbar3 = wx.ToolBar(self.connections, style=wx.TB_TEXT)
		skConnections = self.toolbar3.AddTool(301, _('Add to Signal K'), wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.OnSkConnections, skConnections)
		canConnections = self.toolbar3.AddTool(302, _('Add to CAN Bus'), wx.Bitmap(self.currentdir+"/data/can.png"))
		self.Bind(wx.EVT_TOOL, self.OnCanConnections, canConnections)
		gpsdConnections = self.toolbar3.AddTool(303, _('Add to GPSD'), wx.Bitmap(self.currentdir+"/data/gpsd.png"))
		self.Bind(wx.EVT_TOOL, self.OnGpsdConnections, gpsdConnections)
		pypilotConnections = self.toolbar3.AddTool(304, _('Add to Pypilot'), wx.Bitmap(self.currentdir+"/data/pypilot.png"))
		self.Bind(wx.EVT_TOOL, self.OnPypilotConnections, pypilotConnections)

		self.listConnections = wx.ListCtrl(self.connections, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES, size=(-1,200))
		self.listConnections.InsertColumn(0, _('device')+' /dev/', width=120)
		self.listConnections.InsertColumn(1, _('alias')+' /dev/', width=120)
		self.listConnections.InsertColumn(2, _('data'), width=100)
		self.listConnections.InsertColumn(3, _('connection'), width=100)
		self.listConnections.InsertColumn(4, _('ID'), width=120)
		self.listConnections.InsertColumn(5, _('bauds'), width=100)
		self.listConnections.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListConnectionsSelected)
		self.listConnections.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListConnectionsDeselected)
		self.listConnections.SetTextColour(wx.BLACK)

		self.toolbar4 = wx.ToolBar(self.connections, style=wx.TB_TEXT | wx.TB_VERTICAL)
		editConnection = self.toolbar4.AddTool(401, _('Edit'), wx.Bitmap(self.currentdir+"/data/edit.png"))
		self.Bind(wx.EVT_TOOL, self.OnEditConnection, editConnection)
		removeConnection = self.toolbar4.AddTool(402, _('Remove'), wx.Bitmap(self.currentdir+"/data/cancel.png"))
		self.Bind(wx.EVT_TOOL, self.OnRemoveConnection, removeConnection)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.Add(self.listConnections, 1, wx.ALL | wx.EXPAND, 5)
		hbox.Add(self.toolbar4, 0,  wx.EXPAND, 0)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar3, 0, wx.EXPAND, 0)
		vbox.Add(hbox, 1, wx.EXPAND, 0)

		self.connections.SetSizer(vbox)

	def onListConnectionsSelected(self, e):
		i = e.GetIndex()
		valid = e and i >= 0
		self.onListConnectionsDeselected()
		if not valid: return

		connection = self.listConnections.GetItemText(i, 3)
		if not connection:
			data = self.listConnections.GetItemText(i, 2)
			if data == 'NMEA 0183':
				self.toolbar3.EnableTool(301,True)
				self.toolbar3.EnableTool(303,True)
				self.toolbar3.EnableTool(304,True)
				self.toolbar3.EnableTool(305,True)
			elif data == 'NMEA 2000':
				self.toolbar3.EnableTool(302,True)
			elif data == 'Signal K':
				self.toolbar3.EnableTool(301,True)
		else:
			if connection == 'GPSD': self.toolbar4.EnableTool(401,False)
			else: self.toolbar4.EnableTool(401,True)
			self.toolbar4.EnableTool(402,True)

	def onListConnectionsDeselected(self, e=0):
		self.toolbar3.EnableTool(301,False)
		self.toolbar3.EnableTool(302,False)
		self.toolbar3.EnableTool(303,False)
		self.toolbar3.EnableTool(304,False)
		self.toolbar3.EnableTool(305,False)
		self.toolbar4.EnableTool(401,False)
		self.toolbar4.EnableTool(402,False)

	def OnSkConnections(self,e):
		selected = self.listConnections.GetFirstSelected()
		if selected == -1: return
		if self.platform.skPort: 
			app = 'SK'
			device = self.listConnections.GetItemText(selected, 0)
			alias = self.listConnections.GetItemText(selected, 1)
			data = self.listConnections.GetItemText(selected, 2)
			dlg = addConnection(app,device,alias,data)
			res = dlg.ShowModal()
			if res == wx.ID_SETUP:
				url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/connections/-'
				webbrowser.open(url, new=2)
			elif res == wx.ID_OK:
				if dlg.error: self.ShowStatusBarRED(dlg.error)
				else: 
					if dlg.restart: 
						self.restart_SK(0)
			dlg.Destroy()
		else: 
			self.ShowStatusBarRED(_('Please install "Signal K Installer" OpenPlotter app'))
			self.OnToolSettings()

	def OnCanConnections(self,e):
		selected = self.listConnections.GetFirstSelected()
		if selected == -1: return
		if self.platform.isInstalled('openplotter-can'):
			if self.platform.skPort: 
				app = 'CAN'
				device = self.listConnections.GetItemText(selected, 0)
				alias = self.listConnections.GetItemText(selected, 1)
				data = self.listConnections.GetItemText(selected, 2)
				dlg = addConnection(app,device,alias,data)
				res = dlg.ShowModal()
				if res == wx.ID_SETUP:
					subprocess.call(['pkill', '-f', 'openplotter-can'])
					subprocess.Popen(['openplotter-can', 'canable'])
				elif res == wx.ID_OK:
					if dlg.error: self.ShowStatusBarRED(dlg.error)
					else: 
						if dlg.restart: 
							self.restart_SK(0)
				dlg.Destroy()
			else: 
				self.ShowStatusBarRED(_('Please install "Signal K Installer" OpenPlotter app'))
				self.OnToolSettings()
		else:
			self.ShowStatusBarRED(_('Please install "CAN Bus" OpenPlotter app'))
			self.OnToolSettings()

	def OnGpsdConnections(self,e):
		selected = self.listConnections.GetFirstSelected()
		if selected == -1: return
		if self.platform.isInstalled('gpsd'):
			app = 'gpsd'
			device = self.listConnections.GetItemText(selected, 0)
			alias = self.listConnections.GetItemText(selected, 1)
			data = self.listConnections.GetItemText(selected, 2)
			dlg = addConnection(app,device,alias,data)
			res = dlg.ShowModal()
			if res == wx.ID_OK:
				if dlg.error: self.ShowStatusBarRED(dlg.error)
				else:
					if self.platform.skPort:
						msg = _('Restarting Signal K server... ')
						seconds = 12
						for i in range(seconds, 0, -1):
							self.ShowStatusBarYELLOW(msg+str(i))
							time.sleep(1)
						self.ShowStatusBarGREEN(_('Signal K server restarted'))
					self.read_Serialinst()
			dlg.Destroy()
		else:
			self.ShowStatusBarRED(_('Please install "gpsd" package'))


	def OnPypilotConnections(self,e):
		selected = self.listConnections.GetFirstSelected()
		if selected == -1: return
		if self.platform.isInstalled('openplotter-pypilot'):
			app = 'pypilot'
			device = self.listConnections.GetItemText(selected, 0)
			alias = self.listConnections.GetItemText(selected, 1)
			data = self.listConnections.GetItemText(selected, 2)
			dlg = addConnection(app,device,alias,data)
			res = dlg.ShowModal()
			if res == wx.ID_SETUP:
				subprocess.call(['pkill', '-f', 'openplotter-pypilot'])
				subprocess.Popen(['openplotter-pypilot'])
			elif res == wx.ID_OK:
				if dlg.error: self.ShowStatusBarRED(dlg.error)
				else:
					self.ShowStatusBarYELLOW(_('Applying changes ...'))
					subprocess.call([self.platform.admin, 'python3', self.currentdir+'/service.py', 'pypilot'])
					self.ShowStatusBarGREEN(_('Pypilot serial devices modified and autopilot enabled'))
					self.read_Serialinst()
			dlg.Destroy()
		else:
			self.ShowStatusBarRED(_('Please install "Pypilot" OpenPlotter app'))
			self.OnToolSettings()

	def OnEditConnection(self, e):
		selected = self.listConnections.GetFirstSelected()
		if selected == -1: return
		connection = self.listConnections.GetItemText(selected, 3)
		ID = self.listConnections.GetItemText(selected, 4)
		if connection == 'Signal K':
			if ID:
				url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/connections/'+ID
				webbrowser.open(url, new=2)
		elif connection == 'CAN Bus':
			subprocess.call(['pkill', '-f', 'openplotter-can'])
			subprocess.Popen(['openplotter-can', 'canable'])
		elif connection == 'OpenCPN':
			subprocess.call(['pkill', '-f', 'opencpn'])
			subprocess.Popen(['opencpn'])
		elif connection == 'Pypilot':
			subprocess.call(['pkill', '-f', 'openplotter-pypilot'])
			subprocess.Popen(['openplotter-pypilot'])

	def OnRemoveConnection(self, e):
		selected = self.listConnections.GetFirstSelected()
		if selected == -1: return
		connection = self.listConnections.GetItemText(selected, 3)
		ID = self.listConnections.GetItemText(selected, 4)
		if connection == 'Signal K':
			from openplotterSignalkInstaller import editSettings
			skSettings = editSettings.EditSettings()
			if ID: 
				if skSettings.removeConnection(ID): self.restart_SK(0)
				else: self.ShowStatusBarRED(_('Failed. Error removing connection in Signal K'))
		elif connection == 'CAN Bus':
			subprocess.call(['pkill', '-f', 'openplotter-can'])
			subprocess.Popen(['openplotter-can', 'canable'])
		elif connection == 'GPSD':
			subprocess.call([self.platform.admin, 'python3', self.currentdir+'/editGpsd.py', 'remove', ID])
			if self.platform.skPort:
				msg = _('Restarting Signal K server... ')
				seconds = 12
				for i in range(seconds, 0, -1):
					self.ShowStatusBarYELLOW(msg+str(i))
					time.sleep(1)
				self.ShowStatusBarGREEN(_('Signal K server restarted'))
			self.read_Serialinst()
		elif connection == 'OpenCPN':
			subprocess.call(['pkill', '-f', 'opencpn'])
			subprocess.Popen(['opencpn'])
		elif connection == 'Pypilot':
			subprocess.call(['pkill', '-f', 'openplotter-pypilot'])
			subprocess.Popen(['openplotter-pypilot'])
			
	def restart_SK(self, msg):
		if msg == 0: msg = _('Restarting Signal K server... ')
		seconds = 12
		subprocess.call([self.platform.admin, 'python3', self.currentdir+'/service.py', 'restart'])
		for i in range(seconds, 0, -1):
			self.ShowStatusBarYELLOW(msg+str(i))
			time.sleep(1)
		self.ShowStatusBarGREEN(_('Signal K server restarted'))
		self.read_Serialinst()

################################################################################

class addConnection(wx.Dialog):
	def __init__(self, app, device, alias, data):
		self.conf = conf.Conf()
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		self.ID = alias.replace("ttyOP_", "")
		self.device = '/dev/'+device
		self.alias = '/dev/'+alias
		self.data = data
		self.app = app
		title = _('Adding connection for device: ')+alias
		wx.Dialog.__init__(self, None, title=title, size=(500, 444))
		panel = wx.Panel(self)

		msg1Label = wx.StaticText(panel,-1, style = wx.ALIGN_LEFT) 

		baudsList = ['4800', '9600', '19200', '38400', '57600', '115200', '230400', '460800', '921600']
		baudsLabel = wx.StaticText(panel, label=_('Baud Rate: '))
		self.bauds = wx.ComboBox(panel, choices=baudsList)
		
		msg2Label = rt.RichTextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
		msg2Label.SetMargins((10,10))

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		setupBtn = wx.Button(panel, wx.ID_SETUP, label=_('MANUAL'))
		setupBtn.Bind(wx.EVT_BUTTON, self.setup)
		okBtn = wx.Button(panel, wx.ID_OK, label=_('AUTO'))
		okBtn.Bind(wx.EVT_BUTTON, self.ok)

		if self.app == 'SK':
			msg1 = _('Data: ')+self.data+'\n'
			msg1 += _('ID: ')+self.ID+'\n'
			msg1 += _('Serial port: ')+self.alias
			self.bauds.SetSelection(3)
			msg2Label.WriteText(_('Press AUTO to create a connection in Signal K using the settings above.'))
			msg2Label.Newline()
			msg2Label.Newline()
			msg2Label.WriteText(_('Press MANUAL if you need to add special settings.'))
			msg2Label.Newline()
			msg2Label.Newline()
			msg2Label.WriteText(_('To get data in OpenCPN, make sure this network connection exists in OpenCPN:\nProtocol: Signal K\nAddress: localhost\nDataPort: '+self.platform.skPort+'\nAutomatic server discovery: not'))
		elif self.app == 'CAN':
			msg1 = _('Data: ')+self.data+'\n'
			msg1 += _('ID: ')+self.ID+'\n'
			msg1 += _('Serial port: ')+self.alias
			self.bauds.SetSelection(5)
			msg2Label.WriteText(_('Press AUTO to create a "canboatjs" connection for a NGT-1 or a CAN-USB device in Signal K using the settings above.'))
			msg2Label.Newline()
			msg2Label.Newline()
			msg2Label.WriteText(_('Press MANUAL if you need to add special settings or you want to set a CANable device.'))
			msg2Label.Newline()
			msg2Label.Newline()
			msg2Label.WriteText(_('Use "SK → NMEA 2000" plugin to send data from Signal K to your CAN network. Open desired TX PGNs in your device.'))
			msg2Label.Newline()
			msg2Label.Newline()
			msg2Label.WriteText(_('To get data in OpenCPN, make sure this network connection exists in OpenCPN:\nProtocol: Signal K\nAddress: localhost\nDataPort: '+self.platform.skPort+'\nAutomatic server discovery: not'))
		elif self.app == 'gpsd':
			msg1 = _('Data: ')+self.data+'\n'
			msg1 += _('Serial port: ')+self.alias
			self.bauds.Disable()
			baudsLabel.Disable()
			setupBtn.Disable()
			msg2Label.WriteText(_('Press AUTO to add this device to the list of devices managed by GPSD. A connection for GPSD will be created in Signal K if it does not exist.'))
			msg2Label.Newline()
			msg2Label.Newline()
			msg2Label.WriteText(_('Be sure you send only GNSS or AIS data to GPSD. Baud Rate will be automatically assigned.'))
			msg2Label.Newline()
			msg2Label.Newline()
			msg2Label.WriteText(_('Pypilot will get data from GPSD automatically.'))
		elif self.app == 'pypilot':
			msg1 = _('Data: ')+self.data+' '+ _('(or motor controller data)') +'\n'
			msg1 += _('Serial port: ')+self.alias
			self.bauds.Disable()
			baudsLabel.Disable()
			msg2Label.WriteText(_('Press AUTO to use this device to send data to Pypilot. Baud Rate will be automatically assigned.'))
			msg2Label.Newline()
			msg2Label.Newline()
			msg2Label.WriteText(_('You can also set the motor controller in this way, but make sure you have enabled UART before.'))
			msg2Label.Newline()
			msg2Label.Newline()
			msg2Label.WriteText(_('Press MANUAL if you prefer to set this device in openplotter-pypilot app.'))

		msg1Label.SetLabel(msg1)

		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3.Add(baudsLabel, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 10)
		hbox3.Add(self.bauds, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 10)

		hbox = wx.BoxSizer(wx.HORIZONTAL)
		hbox.AddStretchSpacer(1)
		hbox.Add(cancelBtn, 0, wx.EXPAND, 0)
		hbox.Add(setupBtn, 0, wx.LEFT | wx.EXPAND, 10)
		hbox.Add(okBtn, 0, wx.LEFT | wx.EXPAND, 10)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddSpacer(5)
		vbox.Add(msg1Label, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 15)
		vbox.Add(hbox3, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
		vbox.AddSpacer(5)
		vbox.Add(msg2Label, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 15)
		vbox.Add(hbox, 0, wx.ALL | wx.EXPAND, 10)

		panel.SetSizer(vbox)
		self.panel = panel
		self.Centre() 

	def setup(self,e):
		self.EndModal(wx.ID_SETUP)

	def ok(self,e):
		self.restart = False
		self.error = False
		allSerialPorts = serialPorts.SerialPorts()
		usedSerialPorts = allSerialPorts.getSerialUsedPorts()
		for i in usedSerialPorts:
			if i['id'] == self.ID: self.error = _('Failed. This ID already exists')
			if i['device'] == self.device or i['device'] == self.alias: self.error = _('Failed. This device is already in use')
		if not self.error:
			if self.app == 'SK' or self.app == 'CAN':
				from openplotterSignalkInstaller import editSettings
				skSettings = editSettings.EditSettings()
				c = 0
				while True:
					if skSettings.connectionIdExists(self.ID):
						self.ID = self.ID+str(c)
						c = c + 1
					else: break
				if skSettings.setSerialConnection(self.ID, self.data, self.alias, self.bauds.GetValue()): self.restart = True
				else: self.error = _('Failed. Error creating connection in Signal K')
			elif self.app == 'gpsd':
				subprocess.call([self.platform.admin, 'python3', self.currentdir+'/editGpsd.py', 'add', self.alias])
			elif self.app == 'pypilot':
				exists = False
				path = self.conf.home + '/.pypilot/serial_ports'
				try:
					with open(path, 'r') as f:
						for line in f:
							line = line.replace('\n', '')
							line = line.strip()
							if self.alias == line: exists = True
				except: pass
				if exists: self.error = _('Failed. This device is already set in Pypilot')
				else:
					try:
						with open(path, "a") as file:
							file.write(self.alias + '\n')
					except:	self.error = _('Failed. Error setting the device in Pypilot')

				path = self.conf.home + '/.pypilot/'
				tmp = os.listdir(path)
				for i in tmp:
					if i[:4] == 'nmea' and i[-6:] == 'device':
						subprocess.call(['rm', '-f', path+i])

		self.EndModal(wx.ID_OK)

################################################################################

def main():
	try:
		platform2 = platform.Platform()
		if not platform2.postInstall(version,'serial'):
			subprocess.Popen(['openplotterPostInstall', platform2.admin+' serialPostInstall'])
			return
	except: pass

	app = wx.App()
	SerialFrame().Show()
	time.sleep(1)
	app.MainLoop()

if __name__ == '__main__':
	main()
