#!/bin/bash

# Log installation status
echo "Installing cryptography dependencies..."

# Install on linux operating system
if [[ "$OSTYPE" == "linux"* ]]; then
    sudo apt-get install libffi-dev
fi
