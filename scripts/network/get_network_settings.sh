#!/bin/bash

# Log getting status
printf "Getting network settings...\n\n"

# If NOT the OSX operating system
if [[ "$OSTYPE" != "darwin"* ]]; then
    # Set port forwarding from 80 to 8000
    sudo iptables-restore < /etc/iptables.ipv4.nat
fi


# Explicate path so openssl can find library
export LD_LIBRARY_PATH=/usr/local/lib

# Log network settings
echo LD_LIBRARY_PATH: $LD_LIBRARY_PATH
echo ""
