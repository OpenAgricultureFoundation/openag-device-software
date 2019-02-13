#!/bin/bash

# Log creation status
echo "Creating virtual environment..."

# Check valid command line arguments
if [[ $# -eq 0 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  PROJECT_ROOT (e.g. /home/debian/openag-device-software)"
    exit 1
fi

# Initialize passed in arguments
PROJECT_ROOT=$1

# Install on linux or darwin operating system
if [[ "$OSTYPE" == "linux"* || "$OSTYPE" == "darwin"* ]]; then

    # Check if python (3.6) is installed
    INSTALL_PATH=`which python3.6`
    if [[ ! -f "$INSTALL_PATH" ]]; then
        echo "Unable to create virtual py env, python3.6 is not installed"
        exit 1
    fi

    # Remove any existing virtual environment
    sudo rm -fr $PROJECT_ROOT/venv

    # Create virtual environment
    python3.6 -m venv $PROJECT_ROOT/venv

# Invalid operating system
else
  echo "Unable to create virtual environment, unsupported operating system: $OSTYPE"
  exit 1
fi

