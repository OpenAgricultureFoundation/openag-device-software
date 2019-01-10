#! /bin/bash

# Make sure platform info is sourced
if [[ -z "$PLATFORM" ]]; then
	source get_platform_info.sh > /dev/null 2>&1
fi

# Get wifis for beaglebone wireless
if [[ $PLATFORM == "beaglebone-wireless" ]]; then
	connmanctl tether wifi off > /dev/null 2>&1
	connmanctl enable wifi > /dev/null 2>&1
	connmanctl scan wifi > /dev/null 2>&1
	sleep 2
	connmanctl services

# Get wifis for raspberry pi
elif [[ $PLATFORM == "raspberry-pi"* ]]; then
	sudo iwlist wlan0 scan | egrep 'ESSID:"[^"]' | cut -d ':' -f 2 | sed -e 's/^"//' -e 's/"$//'

# Invalid platform
else
	echo "Wifi not supported for $PLATFORM"
fi
