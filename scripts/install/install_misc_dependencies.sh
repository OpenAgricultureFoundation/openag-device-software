#!/bin/bash

# Log installation status
echo "Installing misc dependencies..."

# Install on linux operating system
if [[ "$OSTYPE" == "linux"* ]]; then

	# For cryptography
    sudo apt-get install libffi-dev -y
fi
