#!/bin/bash

# Log creation status
echo "Creating virtual environment..."

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
        pip3.6 install virtualenv

    fi

    # Remove any existing virtual environment
    rm -fr venv

    # Create virtual environment
    virtualenv -p python3.6 venv

# Invalid operating system
else
  echo "Unable to create virtual environment, unsupported operating system: $OSTYPE"
  exit 1
fi
