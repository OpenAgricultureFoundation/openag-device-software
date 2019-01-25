#!/bin/bash

# Log initialization status
echo "Initializing device config..."

# Check valid command line arguments
if [[ $# -eq 0 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  PROJECT_ROOT (e.g. /home/pi/openag-device-software)"
    exit 1
fi

# Initialize passed in arguments
PROJECT_ROOT=$1

# Initialize device config
echo "unspecified" > $PROJECT_ROOT/data/config/device.txt
