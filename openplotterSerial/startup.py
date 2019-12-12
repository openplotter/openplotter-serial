#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2019 by Sailoog <https://github.com/openplotter/openplotter-serial>
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
		currentdir = os.path.dirname(__file__)
		language.Language(currentdir,'openplotter-serial',currentLanguage)
		allSerialPorts = serialPorts.SerialPorts()
		self.usedSerialPorts = allSerialPorts.getSerialUsedPorts()
		self.initialMessage = _('Checking serial connections alias...')


	def check(self):
		green = _('All your serial connections have an assigned alias')
		black = ''
		red = ''

		for i in self.usedSerialPorts:
			if not 'ttyOP_' in i['device']:
				if not red: red = _('There are serial connections with no alias assigned:')+'\n'+i['app']+' -> '+_('connection ID: ')+i['id']+' | '+_('device: ')+i['device']
				else: red += '\n'+i['app']+' -> '+_('connection ID: ')+i['id']+' | '+_('device: ')+i['device']
				green = ''


		return {'green': green,'black': black,'red': red}

