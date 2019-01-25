#!/bin/bash

# Log initialization status
echo "Inititalizing log level..."

# Check valid command line arguments
if [[ $# -eq 0 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  PROJECT_ROOT (e.g. /home/pi/openag-device-software)"
    echo "  LOG_LEVEL (e.g. DEBUG, INFO, WARNING, ERROR, or CRITICAL)"
    exit 1
elif [[ $# -eq 1 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  LOG_LEVEL (e.g. DEBUG, INFO, WARNING, ERROR, or CRITICAL)"
    exit 1
fi

# Initialize passed in arguments
PROJECT_ROOT=$1
LOG_LEVEL=$2

# Initialize project rc.local
sudo rm -f $PROJECT_ROOT/data/config/rc.local
cp $PROJECT_ROOT/data/config/rc.local.template $PROJECT_ROOT/data/config/rc.local
echo "PROJECT_ROOT=$PROJECT_ROOT" >> $PROJECT_ROOT/data/config/rc.local

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
