#!/bin/bash

# Log persisting status
echo "Persisting remote access..."

# Check valid command line arguments
if [[ $# -eq 0 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  PROJECT_ROOT (e.g. /home/pi/openag-device-software)"
    echo "  REMOTE_DEVICE_UI_URL (e.g. openag-p03q14.serveo.net)"
    echo "  PLATFORM (e.g. raspberry-pi-3)"
    exit 1
elif [[ $# -eq 1 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  REMOTE_DEVICE_UI_URL (e.g. openag-p03q14.serveo.net)"
    echo "  PLATFORM (e.g. raspberry-pi-3)"
    exit 1
elif [[ $# -eq 2 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  PLATFORM (e.g. raspberry-pi-3)"
    exit 1
fi

# Initialize passed in arguments
PROJECT_ROOT=$1
REMOTE_DEVICE_UI_URL=$2

# Check if site is up every 5 minutes else restart forwarding service
while true; do

	# Check if network is online
	ping -c 1 mit.edu > /dev/null 2>&1
	if [[ (! "$?" -eq 0) && ($PLATFORM == "beaglebone-black-wireless") ]]; then
		# E.g. the network connection has changed...
		bash $PROJECT_ROOT/scripts/network/restart_network_connection.sh $PROJECT_ROOT
		sleep 15
	fi	

	# Enable remote access if network is online
	ping -c 1 mit.edu > /dev/null 2>&1
	if [[ "$?" -eq 0 ]]; then
		bash $PROJECT_ROOT/scripts/network/enable_remote_access.sh $REMOTE_DEVICE_UI_URL
		sleep 15
	fi

	# Update every 5 minutes
	sleep 300
	
done
