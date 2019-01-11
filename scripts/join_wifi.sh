#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Please provide the following command line arguments:"
    echo "  wifi ssid (e.g. ElectricElephant)"
    echo "  wifi password (e.g. mysecretpasword)"
    exit 1
fi
if [ $# -eq 1 ]; then
    echo "Please provide the password for the wifi you want to connect to (or '' for no password.)"
    exit 1
fi

# Make sure platform info is sourced
if [[ -z "$PLATFORM" ]]; then
	source $OPENAG_BRAIN_ROOT/scripts/get_platform_info.sh
fi

# Display status information
printf "\nJoining wifi...\n"

# Set wifi credentials
SSID=$1
PASSWORD=$2

# Display wifi credentials
echo SSID: $SSID
echo PASSWORD: $PASSWORD

# Join wifi on a beaglebone
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

# Join wifi on a raspberry pi
elif [[ $PLATFORM == "raspberry-pi"* ]]; then

	# Append network config to wpa supplicant config file
	NETWORK_STRING=$'\n'"network={"$'\n\t'"ssid="$'"'"${SSID}"$'"'$'\n\t'"psk="$'"'"${PASSWORD}"$'"'$'\n'"}"$'\n'
	sudo echo "${NETWORK_STRING}" >> /etc/wpa_supplicant/wpa_supplicant.conf

	# Disable wifi access point
	echo "Disabling access point..."
	bash $OPENAG_BRAIN_ROOT/scripts/disable_raspi_access_point.sh
	sleep 3

	# Restart wifi connection
	echo "Restarting wifi connection..."
	wpa_cli -i wlan0 reconfigure

# Invalid platform
else
	echo "Wifi not supported for $PLATFORM"
	exit 0
fi

# Restart port forwarding
echo "Restarting port forwarding..."
bash $OPENAG_BRAIN_ROOT/scripts/forward_ports.sh
