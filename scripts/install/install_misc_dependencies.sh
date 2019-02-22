#!/bin/bash

# Log installation status
echo "Installing misc dependencies..."

# Install on linux operating system
if [[ "$OSTYPE" == "linux"* ]]; then

	# For cryptography
    sudo apt-get install libffi-dev -y

	# For USB-I2C cable
    sudo apt-get install libusb-1.0 -y

# Install on OSX operating system
elif [[ "$OSTYPE" == "darwin"* ]]; then

	# For USB-I2C cable
    brew install libusb
fi
