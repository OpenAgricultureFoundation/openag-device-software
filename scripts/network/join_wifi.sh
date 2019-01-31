#! /bin/bash

# Ensure virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]] ; then
    echo "Please activate your virtual environment then re-run script"
    exit 1
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
	bash $PROJECT_ROOT/scripts/network/join_wifi_beaglebone.sh $SSID $PASSWORD

# Join wifi on a raspberry pi
elif [[ $PLATFORM == "raspberry-pi"* ]]; then
	bash $PROJECT_ROOT/scripts/network/join_wifi_raspi.sh $SSID $PASSWORD

# Invalid platform
else
	echo "Unable to join wifi, wifi not supported for $PLATFORM"
	exit 0
fi

# Restart port forwarding
echo "Restarting remote access..."
bash $PROJECT_ROOT/scripts/network/enable_remote_access.sh $REMOTE_DEVICE_UI_URL
