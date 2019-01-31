#! /bin/bash

# Ensure virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]] ; then
    echo "Please activate your virtual environment then re-run script"
    exit 1
fi

# Get wifi ssids for beaglebone wireless
if [[ $PLATFORM == "beaglebone-black-wireless" ]]; then
	bash $PROJECT_ROOT/scripts/network/get_wifi_ssids_beaglebone.sh $SSID $PASSWORD

# Get wifi ssids for raspberry pi
elif [[ $PLATFORM == "raspberry-pi"* ]]; then
	bash $PROJECT_ROOT/scripts/network/get_wifi_ssids_raspi.sh $SSID $PASSWORD

# Invalid platform
else
	echo "Wifi not supported for $PLATFORM"
fi
