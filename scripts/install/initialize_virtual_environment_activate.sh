#!/bin/bash

# Check valid command line arguments
if [ $# -eq 0 ]; then
    echo "Please provide the following command line arguments:"
    echo "  PROJECT_ROOT (e.g. /home/pi/openag-device-software)"
    exit 1
fi

# Initialize passed in arguments
PROJECT_ROOT=$1

# Set project root as environment variable in virtual environment
printf "\n# Set project root\n" >> $PROJECT_ROOT/venv/bin/activate
echo "export PROJECT_ROOT=$PROJECT_ROOT" >> $PROJECT_ROOT/venv/bin/activate

# Set platform environment variables in virtual environment
printf "\n# Source project activate file\n" >> $PROJECT_ROOT/venv/bin/activate
echo "source $PROJECT_ROOT/scripts/install/activate.sh" >> $PROJECT_ROOT/venv/bin/activate
