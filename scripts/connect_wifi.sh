#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Please provide the following command line arguments:"
    echo "  wifi_<...> (beaglebone) | <ssid> (raspi) name you want to connect to,"
    echo "  password of the wifi you want to connect to."
    exit 1
fi
if [ $# -eq 1 ]; then
    echo "Please provide the password for the wifi you want to connect to (or '' for no password."
    exit 1
fi

# Make sure platform info is sourced
if [[ -z "$PLATFORM" ]]; then
	source get_platform_info.sh
fi

printf "\nConnecting to wifi...\n\n"

# Connect to wifi on a beaglebone
if [[ $PLATFORM == "beaglebone-wireless" ]]; then
	 
	# Get the SSID for this service
	SSID=`connmanctl services $1 | grep "Name =" | cut --delimiter=' ' --fields 5-10`
	SSIDLEN=`echo -n $SSID | wc -m`
	if [ $SSIDLEN -eq 0 ]; then
	    echo "Can't connect to a wifi with a hidden SSID, sorry.  Use connmanctl"
	    exit 1
	fi
	 
	touch "/var/lib/connman/$SSID.config.tmp"
	chmod 777 "/var/lib/connman/$SSID.config.tmp"
	echo "[service_$1]
	Type=wifi
	Name=$SSID
	Passphrase=$2
	"> "/var/lib/connman/$SSID.config.tmp"
	mv "/var/lib/connman/$SSID.config.tmp" "/var/lib/connman/$SSID.config"
	sleep 30
	 
	echo "Using sudo to configure your networking, please enter your password:"
	sudo service connman restart

# Connect to wifi on a raspberry pi
elif [[ $PLATFORM == "raspberry-pi"* ]]; then

	# Set wifi credentials
	SSID=$1
	PSK=$2

	# Display wifi credentials
	echo SSID: $SSID
	echo PSK: $PSK

	# Append network config to wpa supplicant config file
	NETWORK_STRING=$'\n'"network={"$'\n\t'"ssid="$'"'"${SSID}"$'"'$'\n\t'"psk="$'"'"${PSK}"$'"'$'\n'"}"$'\n'
	sudo echo "${NETWORK_STRING}" >> /etc/wpa_supplicant/wpa_supplicant.conf

	# Restart wifi connection
	printf "\nRestarting wifi connection...\n\n"
	wpa_cli -i wlan0 reconfigure

# Invalid platform
else
	echo "Wifi not supported for $PLATFORM"
	return
fi

# We must restart autossh, otherwise serveo.net won't let us back in.
printf "\nRestarting autossh...\n\n"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
bash $DIR/forward_ports.sh &
