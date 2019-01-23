#!/bin/bash

# Log update status
echo "Updating operating system..."

# Install on linux linux operating system
if [[ "$OSTYPE" == "linux"* ]]; then
    sudo apt-get update -y
    sudo apt-get upgrade -y

# Install on darwin operating system
elif [[ "$OSTYPE" == "darwin"* ]]; then
	exit 0    

# Invalid operating system
else
  echo "Unable to update, unsupported operating system: $OSTYPE"
  exit 1
fi
