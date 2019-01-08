#!/bin/bash

# TODO: This is a bad way to do this. Move to python.

# Get beaglebone serial number
serial=`sudo hexdump -e '8/1 "%c"' "/sys/bus/i2c/devices/0-0050/eeprom" -s 16 -n 12 2>&1`

# So cringy...
# Get raspberry pi serial number if beagle s/n failed
if [[ $serial == *"hexdump"* ]]; then
	# Get raspberry pi serial number
	serial=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`
fi

# Build url
url=$serial.serveo.net

# Check if site is up
wget --server-response --spider $url > /dev/null 2>&1
if [ "$?" -eq 0 ]
then
	echo 'Site is up'
	
else
	echo 'Site is down'
fi
