#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2019 by e-sailing <https://github.com/openplotter/openplotter-serial>
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

from setuptools import setup
from openplotterSerial import version

setup (
	name = 'openplotterSerial',
	version = version.version,
	description = 'OpenPlotter app to manage serial devices',
	license = 'GPLv3',
	author="e-sailing",
	author_email='e.minus.sailing@gmail.com',
	url='https://github.com/openplotter/openplotter-serial',
	packages=['openplotterSerial'],
	classifiers = ['Natural Language :: English',
	'Operating System :: POSIX :: Linux',
	'Programming Language :: Python :: 3'],
	include_package_data=True,
	entry_points={'console_scripts': ['openplotter-serial=openplotterSerial.openplotterSerial:main']},
	data_files=[('share/applications', ['openplotterSerial/data/openplotter-serial.desktop']),('share/pixmaps', ['openplotterSerial/data/openplotter-serial.png']),],
	)
