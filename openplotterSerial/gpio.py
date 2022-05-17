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
import subprocess, sys

class Gpio:
	def __init__(self,conf):
		self.conf = conf
		self.used = [] # {'app':'xxx', 'id':'xxx', 'physical':'n'}

	def usedGpios(self):

		try: config = open('/boot/config.txt', 'r')
		except:
			try: config = open('/boot/firmware/config.txt', 'r')
			except: config = ''
		if config:
			data = config.read()
			config.close()

		gpiotx = ''
		gpiorx = ''
		if 'enable_uart=0' in data and not '#enable_uart=0' in data: pass
		else:
			try: subprocess.check_output(['systemctl', 'is-active', 'hciuart']).decode(sys.stdin.encoding)	
			except: 
				gpiotx = {'app':'Serial', 'id':'UART0 TX', 'physical':'8'}
				gpiorx = {'app':'Serial', 'id':'UART0 RX', 'physical':'10'}
			else:
				if 'enable_uart=1' in data and not '#enable_uart=1' in data:
					gpiotx = {'app':'Serial', 'id':'UART1 TX', 'physical':'8'}
					gpiorx = {'app':'Serial', 'id':'UART1 RX', 'physical':'10'}
		if gpiotx: self.used.append(gpiotx)
		if gpiorx: self.used.append(gpiorx)

		if 'dtoverlay=uart2' in data and not '#dtoverlay=uart2' in data:
			self.used.append({'app':'Serial', 'id':'UART2 TX', 'physical':'27'})
			self.used.append({'app':'Serial', 'id':'UART2 RX', 'physical':'28'})

		if 'dtoverlay=uart3' in data and not '#dtoverlay=uart3' in data:
			self.used.append({'app':'Serial', 'id':'UART3 TX', 'physical':'7'})
			self.used.append({'app':'Serial', 'id':'UART3 RX', 'physical':'29'})

		if 'dtoverlay=uart4' in data and not '#dtoverlay=uart4' in data:
			self.used.append({'app':'Serial', 'id':'UART4 TX', 'physical':'24'})
			self.used.append({'app':'Serial', 'id':'UART4 RX', 'physical':'21'})

		if 'dtoverlay=uart5' in data and not '#dtoverlay=uart5' in data:
			self.used.append({'app':'Serial', 'id':'UART5 TX', 'physical':'32'})
			self.used.append({'app':'Serial', 'id':'UART5 RX', 'physical':'33'})

		return self.used