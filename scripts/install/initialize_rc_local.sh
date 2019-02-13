#!/bin/bash

# Log initialization status
echo "Inititalizing rc.local..."

# Do nothing on OSX operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    exit 0    
fi

# Check valid command line arguments
if [[ $# -eq 0 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  PROJECT_ROOT (e.g. /home/pi/openag-device-software)"
    echo "  RUNTIME_MODE (e.g. DEVELOPMENT or PRODUCTION)"
    echo "  REMOTE_DEVICE_UI_URL (e.g. openag-pq485.serveo.net)"
    echo "  PLATFORM (e.g. raspberry-pi-3)"
    exit 1
elif [[ $# -eq 1 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  RUNTIME_MODE (e.g. DEVELOPMENT or PRODUCTION)"
    echo "  REMOTE_DEVICE_UI_URL (e.g. openag-pq485.serveo.net)"
    echo "  PLATFORM (e.g. raspberry-pi-3)"
    exit 1
elif [[ $# -eq 2 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  REMOTE_DEVICE_UI_URL (e.g. openag-pq485.serveo.net)"
    echo "  PLATFORM (e.g. raspberry-pi-3)"
    exit 1
elif [[ $# -eq 3 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  PLATFORM (e.g. raspberry-pi-3)"
    exit 1
fi

# Initialize passed in arguments
PROJECT_ROOT=$1
RUNTIME_MODE=$2
REMOTE_DEVICE_UI_URL=$3
PLATFORM=$4

# Initialize project rc.local
sudo rm -f $PROJECT_ROOT/data/config/rc.local
cp $PROJECT_ROOT/data/config/rc.local.template $PROJECT_ROOT/data/config/rc.local
echo "PROJECT_ROOT=$PROJECT_ROOT" >> $PROJECT_ROOT/data/config/rc.local
echo "REMOTE_DEVICE_UI_URL=$REMOTE_DEVICE_UI_URL" >> $PROJECT_ROOT/data/config/rc.local
echo "PLATFORM=$PLATFORM" >> $PROJECT_ROOT/data/config/rc.local

# Set rc.local for production
if [[ "$RUNTIME_MODE" == "PRODUCTION" ]]; then
	cat $PROJECT_ROOT/data/config/rc.local.production >> $PROJECT_ROOT/data/config/rc.local
elif [[ "$RUNTIME_MODE" == "DEVELOPMENT" ]]; then
	cat $PROJECT_ROOT/data/config/rc.local.development >> $PROJECT_ROOT/data/config/rc.local
else
	echo "Unable to initialize rc.local, invalid runtime mode"
	exit 1
fi
 
# Symlink system rc.local to project rc.local
sudo rm -f /etc/rc.local 
sudo ln -s $PROJECT_ROOT/data/config/rc.local /etc/rc.local

# Restart rc.local service
sudo service rc.local restart
