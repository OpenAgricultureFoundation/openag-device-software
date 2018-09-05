#!/bin/bash

# Get beaglebone serial number
serial=`sudo hexdump -e '8/1 "%c"' "/sys/bus/i2c/devices/0-0050/eeprom" -s 16 -n 12 2>&1`

# Build url
url=$serial.serveo.net

# Check if site is up
wget --server-response --spider $url > /dev/null 2>&1
if [ "$?" -eq 0 ]
then
	echo 'Site is up'	
else
	echo 'Site is down, restarting'
	serial=`sudo hexdump -e '8/1 "%c"' "/sys/bus/i2c/devices/0-0050/eeprom" -s 16 -n 12 2>&1`
	sudo killall -s 9 autossh > /dev/null 2>&1
	autossh -M 0 -R $serial.serveo.net:80:localhost:80 serveo.net -R $serial:22:localhost:22 serveo.net -oServerAliveInterval=30 -oStrictHostKeyChecking=no -f
fi
