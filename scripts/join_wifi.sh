#! /bin/bash

# Check virtual environment is activated
if [ -z "${VIRTUAL_ENV}" ] ; then
    echo "Please activate your virtual environment then re-run script"
    exit 0
fi

# Check platform info is sourced
if [[ -z "$PLATFORM" ]]; then
	source $OPENAG_BRAIN_ROOT/scripts/get_platform_info.sh
fi

# Get command line args
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


# Display status information
echo "Joining wifi..."

# Set wifi credentials
SSID=$1
PASSWORD=$2

# Display wifi credentials
echo SSID: $SSID
echo PASSWORD: $PASSWORD

# Join wifi on a beaglebone
if [[ $PLATFORM == "beaglebone-black-wireless" ]]; then
	 
	touch "/var/lib/connman/$SSID.config.tmp"
	chmod 777 "/var/lib/connman/$SSID.config.tmp"
	echo "[service_$1]
	Type=wifi
	Name=$SSID
	Passphrase=$PASSWORD
	"> "/var/lib/connman/$SSID.config.tmp"
	mv "/var/lib/connman/$SSID.config.tmp" "/var/lib/connman/$SSID.config"
	sleep 3
	sudo service connman restart
	sleep 3

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
	sleep 3

# Invalid platform
else
	echo "Unable to join wifi, wifi not supported for $PLATFORM"
	exit 0
fi

# Restart port forwarding
echo "Restarting port forwarding..."
bash $OPENAG_BRAIN_ROOT/scripts/forward_ports.sh
