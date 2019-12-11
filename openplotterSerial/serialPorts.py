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

class SerialPorts:
	def __init__(self,conf):
		self.conf = conf
		self.connections = []
		# {'app':'xxx', 'id':'xxx', 'data':'NMEA0183/NMEA2000/SignalK', 'device': '/dev/xxx', "baudrate": nnnnnn, "enabled": True/False}

	def usedSerialPorts(self):
		devList = []
		try:
			with open('/etc/default/gpsd', 'r') as f:
				for line in f:
					if 'DEVICES=' in line:
						line = line.replace('\n', '')
						line = line.strip()
						items = line.split('=')
						item1 = items[1].replace('"', '')
						item1 = item1.strip()
						devList = item1.split(' ')
		except:pass
		for i in devList:
			if i:
				self.connections.append({'app':'GPSD','id':i, 'data':'NMEA0183', 'device': i, 'baudrate': 'auto', "enabled": True})
		return self.connections