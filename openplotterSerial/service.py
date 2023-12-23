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

import sys, subprocess, os

def edit_boot(onoff):
	try:
		config = '/boot/firmware/config.txt'
		os.system('cp -f '+config+' '+config+'_back')
		file = open(config, 'r')
	except:
		try:
			config = '/boot/config.txt'
			os.system('cp -f '+config+' '+config+'_back')
			file = open(config, 'r')
		except Exception as e:
			print(str(e))
			return
	exists = False
	out = ''
	while True:
		line = file.readline()
		if not line: break
		if onoff and 'dtoverlay=disable-bt' in line: 
			out += 'dtoverlay=disable-bt\n'
			os.system('systemctl disable hciuart')
			exists = True
		elif not onoff and 'dtoverlay=disable-bt' in line: 
			os.system('systemctl enable hciuart')
		elif 'enable_uart=' in line: pass
		else: out += line
	if onoff and not exists: 
		out += 'dtoverlay=disable-bt\n'
		os.system('systemctl disable hciuart')
	file.close()
	try: 
		file = open(config, 'w')
		file.write(out)
		file.close()
	except Exception as e:
		os.system('cp -f '+config+'_back '+config)
		print(str(e))
		return

	try:
		cmdline = '/boot/firmware/cmdline.txt'
		os.system('cp -f '+cmdline+' '+cmdline+'_back')
		file = open(cmdline, 'r')
	except:
		try:
			cmdline = '/boot/cmdline.txt'
			os.system('cp -f '+cmdline+' '+cmdline+'_back')
			file = open(cmdline, 'r')
		except Exception as e:
			print(str(e))
			return
	text = file.read()
	text = text.replace('\n', '')
	text_list = text.split(' ')
	if onoff and 'console=serial0,115200' in text_list: 
		text_list.remove('console=serial0,115200')
	final = ' '.join(text_list)+'\n'
	file.close()
	try: 
		file = open(cmdline, 'w')
		file.write(final)
		file.close()
	except Exception as e:
		os.system('cp -f '+cmdline+'_back '+cmdline)
		print(str(e))
		return

def edit_boot2(onoff, i):
	try:
		config = '/boot/firmware/config.txt'
		os.system('cp -f '+config+' '+config+'_back')
		file = open(config, 'r')
	except:
		try:
			config = '/boot/config.txt'
			os.system('cp -f '+config+' '+config+'_back')
			file = open(config, 'r')
		except Exception as e:
			print(str(e))
			return
	exists = False
	out = ''
	while True:
		line = file.readline()
		if not line: break
		if onoff and 'dtoverlay=uart'+i in line: 
			out += 'dtoverlay=uart'+i+'\n'
			exists = True
		elif not onoff and 'dtoverlay=uart'+i in line: pass
		else: out += line
	if onoff and not exists: out += 'dtoverlay=uart'+i+'\n'
	file.close()
	try: 
		file = open(config, 'w')
		file.write(out)
		file.close()
	except Exception as e:
		os.system('cp -f '+config+'_back '+config)
		print(str(e))
		return

def edit_boot3(onoff, i):
	try:
		config = '/boot/firmware/config.txt'
		os.system('cp -f '+config+' '+config+'_back')
		file = open(config, 'r')
	except:
		try:
			config = '/boot/config.txt'
			os.system('cp -f '+config+' '+config+'_back')
			file = open(config, 'r')
		except Exception as e:
			print(str(e))
			return
	exists = False
	out = ''
	while True:
		line = file.readline()
		if not line: break
		if onoff and 'dtoverlay=uart'+i+'-pi5' in line: 
			out += 'dtoverlay=uart'+i+'-pi5\n'
			exists = True
		elif not onoff and 'dtoverlay=uart'+i+'-pi5' in line: pass
		else: out += line
	if onoff and not exists: out += 'dtoverlay=uart'+i+'-pi5\n'
	file.close()
	try: 
		file = open(config, 'w')
		file.write(out)
		file.close()
	except Exception as e:
		os.system('cp -f '+config+'_back '+config)
		print(str(e))
		return

def edit_boot1(onoff):
	try:
		config = '/boot/firmware/config.txt'
		os.system('cp -f '+config+' '+config+'_back')
		file = open(config, 'r')
	except:
		try:
			config = '/boot/config.txt'
			os.system('cp -f '+config+' '+config+'_back')
			file = open(config, 'r')
		except Exception as e:
			print(str(e))
			return
	exists = False
	out = ''
	while True:
		line = file.readline()
		if not line: break
		if onoff and 'dtparam=uart0=on' in line: 
			out += 'dtparam=uart0=on\n'
			exists = True
		elif not onoff and 'dtparam=uart0=on' in line: pass
		else: out += line
	if onoff and not exists: out += 'dtparam=uart0=on\n'
	file.close()
	try: 
		file = open(config, 'w')
		file.write(out)
		file.close()
	except Exception as e:
		os.system('cp -f '+config+'_back '+config)
		print(str(e))
		return

if sys.argv[1]=='start':
	subprocess.call(['systemctl', 'start', 'signalk.socket'])
	subprocess.call(['systemctl', 'start', 'signalk.service'])

elif sys.argv[1]=='stop':
	subprocess.call(['systemctl', 'stop', 'signalk.service'])
	subprocess.call(['systemctl', 'stop', 'signalk.socket'])

elif sys.argv[1]=='restart':
	subprocess.call(['systemctl', 'stop', 'signalk.service'])
	subprocess.call(['systemctl', 'stop', 'signalk.socket'])
	subprocess.call(['systemctl', 'start', 'signalk.socket'])
	subprocess.call(['systemctl', 'start', 'signalk.service'])

elif sys.argv[1]=='udev':
	path = sys.argv[2]
	os.system('mv '+path+' /etc/udev/rules.d')
	subprocess.call(['udevadm', 'control', '--reload-rules'])
	subprocess.call(['udevadm', 'trigger', '--attr-match=subsystem=tty'])

elif sys.argv[1]=='uartTrue': edit_boot(True)
elif sys.argv[1]=='uartFalse': edit_boot(False)

elif sys.argv[1]=='uart2True': edit_boot2(True,'2')
elif sys.argv[1]=='uart2False': edit_boot2(False,'2')
elif sys.argv[1]=='uart3True': edit_boot2(True,'3')
elif sys.argv[1]=='uart3False': edit_boot2(False,'3')
elif sys.argv[1]=='uart4True': edit_boot2(True,'4')
elif sys.argv[1]=='uart4False': edit_boot2(False,'4')
elif sys.argv[1]=='uart5True': edit_boot2(True,'5')
elif sys.argv[1]=='uart5False': edit_boot2(False,'5')

elif sys.argv[1]=='uartTruePi5': edit_boot1(True)
elif sys.argv[1]=='uartFalsePi5': edit_boot1(False)

elif sys.argv[1]=='uart1TruePi5': edit_boot3(True,'1')
elif sys.argv[1]=='uart1FalsePi5': edit_boot3(False,'1')
elif sys.argv[1]=='uart2TruePi5': edit_boot3(True,'2')
elif sys.argv[1]=='uart2FalsePi5': edit_boot3(False,'2')
elif sys.argv[1]=='uart3TruePi5': edit_boot3(True,'3')
elif sys.argv[1]=='uart3FalsePi5': edit_boot3(False,'3')
elif sys.argv[1]=='uart4TruePi5': edit_boot3(True,'4')
elif sys.argv[1]=='uart4FalsePi5': edit_boot3(False,'4')
