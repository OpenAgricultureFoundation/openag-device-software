#! /bin/bash

# Ensure virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]] ; then
    echo "Please activate your virtual environment then re-run script"
    exit 1
fi

# Get wifi ssids for beaglebone wireless
if [[ $PLATFORM == "beaglebone-black-wireless" ]]; then
	connmanctl tether wifi off > /dev/null 2>&1
	connmanctl enable wifi > /dev/null 2>&1
	connmanctl scan wifi > /dev/null 2>&1
	sleep 2
	connmanctl services | sed -e 's/wifi_[^ ]*//' -e 's/ *//' | grep '\w\w*'


# Get wifi ssids for raspberry pi
elif [[ $PLATFORM == "raspberry-pi"* ]]; then
	sudo iwlist wlan0 scan | egrep 'ESSID:"[^"]' | cut -d ':' -f 2 | sed -e 's/^"//' -e 's/"$//'

# Invalid platform
else
	echo "Wifi not supported for $PLATFORM"
fi
