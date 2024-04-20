#!/usr/bin/env python3

# This file is part of OpenPlotter.
# Copyright (C) 2019 by e-sailing <https://github.com/openplotter/openplotter-serial>
#               2022 by Sailoog <https://github.com/openplotter/openplotter-serial>
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

import os, subprocess
from openplotterSettings import conf
from openplotterSettings import language
from .version import version

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	language.Language(currentdir,'openplotter-serial',currentLanguage)

	print(_('Editing GPSD config file...'))
	try:
		path = '/etc/default/gpsd'
		if not os.path.exists(path):
			fo = open(path, "w")
			fo.write( 'START_DAEMON="false"\nUSBAUTO="false"\nDEVICES=""\nGPSD_OPTIONS="-n -b"')
			fo.close()
		else:
			subprocess.call(['sed', '-i', 's/USBAUTO="true"/USBAUTO="false"/g', '/etc/default/gpsd'])
			subprocess.call(['sed', '-i', 's/USBAUTO = "true"/USBAUTO = "false"/g', '/etc/default/gpsd'])
			devList = []
			daemon = False
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
			if not devList and daemon:
				subprocess.call(['sed', '-i', 's/START_DAEMON="true"/START_DAEMON="false"/g', '/etc/default/gpsd'])
				subprocess.call(['sed', '-i', 's/START_DAEMON = "true"/START_DAEMON = "false"/g', '/etc/default/gpsd'])

		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Setting version...'))
	try:
		conf2.set('APPS', 'serial', version)
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()
