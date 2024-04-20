#!/usr/bin/env python3

# This file is part of OpenPlotter.
# Copyright (C) 2022 by Sailoog <https://github.com/openplotter/openplotter-serial>
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

import subprocess, os
from openplotterSettings import language
from openplotterSettings import serialPorts

class Start():
	def __init__(self, conf, currentLanguage):
		self.initialMessage = ''

		
	def start(self):
		green = ''
		black = ''
		red = ''

		return {'green': green,'black': black,'red': red}

class Check():
	def __init__(self, conf, currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-serial',currentLanguage)
		allSerialPorts = serialPorts.SerialPorts()
		self.usedSerialPorts = allSerialPorts.getSerialUsedPorts()
		self.initialMessage = _('Checking serial connections alias...')


	def check(self):
		green = ''
		black = _('All your serial connections have an assigned alias')
		red = ''

		for i in self.usedSerialPorts:
			if not 'ttyOP_' in i['device']:
				if not red: red = _('There are serial connections with no alias assigned:')+'\n   '+i['app']+' -> '+_('connection ID: ')+i['id']+' | '+_('device: ')+i['device']
				else: red += '\n   '+i['app']+' -> '+_('connection ID: ')+i['id']+' | '+_('device: ')+i['device']
				black = ''

		devList = []
		daemon = False
		usbauto = False
		with open('/etc/default/gpsd', 'r') as f:
			for line in f:
				if 'DEVICES=' in line:
					line = line.replace('\n', '')
					line = line.strip()
					items = line.split('=')
					item1 = items[1].replace('"', '')
					item1 = item1.strip()
					devList = item1.split(' ')
				if 'START_DAEMON=' in line:
					if 'true' in line: daemon = True
				if 'USBAUTO=' in line:
					if 'true' in line: usbauto = True

		if usbauto:
			msg = _('Set USBAUTO="false" in /etc/default/gpsd')
			if red: red += '\n   '+msg
			else: red = msg

		if not devList and daemon:
			msg = _('Set START_DAEMON="false" in /etc/default/gpsd')
			if red: red += '\n   '+msg
			else: red = msg

		return {'green': green,'black': black,'red': red}

