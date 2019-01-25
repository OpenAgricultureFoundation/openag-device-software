#!/bin/bash

# Log initialization status
echo "Initializing directory structure..."

# Check valid command line arguments
if [[ $# -eq 0 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  PROJECT_ROOT (e.g. /home/pi/openag-device-software)"
    exit 1
fi

# Initialize passed in arguments
PROJECT_ROOT=$1

# Initialize directory structure
sudo mkdir -p $PROJECT_ROOT/data/images/stored
