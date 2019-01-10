#!/bin/bash

echo "Checking ports..."

# Check if site is up
wget --server-response --spider $REMOTE_DEVICE_UI_URL -T 3 -t 2 > /dev/null 2>&1
if [ "$?" -eq 0 ]
then
	echo 'Site is up'
	
else
	echo 'Site is down'
fi
