#! /bin/bash

# Log enabling status
echo "Enabling remote access..."

# Check valid command line arguments
if [[ $# -eq 0 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  REMOTE_DEVICE_UI_URL (e.g. openag-p03q14.serveo.net)"
    exit 1
fi

# Initialize passed in arguments
REMOTE_DEVICE_UI_URL=$1

# Check network connection
ping -c 1 mit.edu > /dev/null 2>&1
if [ ! "$?" -eq 0 ]; then
	echo "Unable to enable remote access, network is down"
	exit 1
fi	

# Check remote device ui connection
wget --server-response --spider $REMOTE_DEVICE_UI_URL -T 3 -t 2 > /dev/null 2>&1
if [ "$?" -eq 0 ]; then
	echo "Remote device ui already online"
	exit 1
fi

# Get remote device ui prefix
REMOTE_DEVICE_UI_PREFIX=${REMOTE_DEVICE_UI_URL%".serveo.net"}

# Restart autossh forwarding
sudo killall -s 9 autossh > /dev/null 2>&1
autossh -M 0 -R $REMOTE_DEVICE_UI_PREFIX:80:localhost:8000 serveo.net -R $REMOTE_DEVICE_UI_PREFIX:22:localhost:22 serveo.net -oServerAliveInterval=30 -oStrictHostKeyChecking=no -f
