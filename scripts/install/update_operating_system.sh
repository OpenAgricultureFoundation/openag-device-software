#!/bin/bash

# Log update status
echo "Updating operating system..."

# Update the linux operating system packages
if [[ "$OSTYPE" == "linux"* ]]; then
    sudo apt-get update -y

# Install on darwin operating system
elif [[ "$OSTYPE" == "darwin"* ]]; then
	exit 0    

# Invalid operating system
else
  echo "Unable to update, unsupported operating system: $OSTYPE"
  exit 1
fi
