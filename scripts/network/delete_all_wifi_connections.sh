#! /bin/bash

# Check virtual environment is activated
if [ -z "${VIRTUAL_ENV}" ] ; then
    echo "Please activate your virtual environment then re-run script"
    exit 0
fi

# Delete all wifi connections
echo "Deleting all wifi connections..."

# Delete wifi connections for beaglebone black wireless
if [[ $PLATFORM == "beaglebone-black-wireless" ]]; then
	sudo service connman stop
	sleep 3
	sudo rm -fr /var/lib/connman/*.config /var/lib/connman/wifi_*
	sudo service connman start

# Delete wifi connections for raspberry pi
elif [[ $PLATFORM == "raspberry-pi"* ]]; then
	echo "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev" > /etc/wpa_supplicant/wpa_supplicant.conf
	echo "update_config=1" >> /etc/wpa_supplicant/wpa_supplicant.conf
	sudo systemctl daemon-reload
	sudo systemctl restart dhcpcd

# Invalid platform
else
	echo "Unable to delete all wifi connections, wifi not supported for $PLATFORM"
	exit 0
fi
