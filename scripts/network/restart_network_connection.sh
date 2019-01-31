#! /bin/bash

# Log restarting status
echo "Restarting network connection..."

# Check valid command line arguments
if [[ $# -eq 0 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  PROJECT_ROOT (e.g. /home/pi/openag-device-software)"
    exit 1
fi

# Initialize passed in arguments
PROJECT_ROOT=$1

# Ensure platform is defined
if [[ -z "$PLATFORM" ]]; then
	source $PROJECT_ROOT/scripts/platform/get_platform_info.sh
	echo $PLATFORM
fi

# Check if platform still not defined
if [[ -z "$PLATFORM" ]]; then
	echo "Unable to restart network, platform is not defined"
	exit 1
fi

# Only restart network for beaglebone blacks now
if [[ "$PLATFORM" == "beaglebone-black"* ]]; then
	sudo service connman restart > /dev/null 2>&1
elif [[ "$PLATFORM" == "raspberry-pi"* ]]; then
	sudo systemctl daemon-reload
	sudo systemctl restart dhcpcd
else
	echo "Unable to restart network, unsupported platform $PLATFORM"
fi
