#!/bin/bash

# Log creation status
echo "Creating virtual environment..."

# Check valid command line arguments
if [[ $# -eq 0 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  PROJECT_ROOT (e.g. /home/pi/openag-device-software)"
    exit 1
fi

# Initialize passed in arguments
PROJECT_ROOT=$1

# Install on linux or darwin operating system
if [[ "$OSTYPE" == "linux"* || "$OSTYPE" == "darwin"* ]]; then

    # Ensure virtualenv is installed
    INSTALL_PATH=`which virtualenv`
    if [[ ! -f "$INSTALL_PATH" ]]; then
        
        # Log install status
        echo "Installing virtualenv..."

        # Check pip3.6 is installed
        INSTALL_PATH=`which pip3.6`
        if [[ ! -f "$INSTALL_PATH" ]]; then
            echo "Unable to install virtualenv, pip3.6 is not installed"
            exit 1
        fi

        # Install virtualenv
        sudo pip3.6 install virtualenv

    fi

    # Remove any existing virtual environment
    sudo rm -fr $PROJECT_ROOT/venv

    # Create virtual environment
    virtualenv -p python3.6 $PROJECT_ROOT/venv

# Invalid operating system
else
  echo "Unable to create virtual environment, unsupported operating system: $OSTYPE"
  exit 1
fi

