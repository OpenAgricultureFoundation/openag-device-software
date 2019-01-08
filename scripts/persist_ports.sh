#!/bin/bash

# TODO: This is a bad way to do this, move to python.

# Get beaglebone serial number
serial=`sudo hexdump -e '8/1 "%c"' "/sys/bus/i2c/devices/0-0050/eeprom" -s 16 -n 12 2>&1`

# So cringy...
# Get raspberry pi serial number if beagle s/n failed
if [[ $serial == *"hexdump"* ]]; then
	# Get raspberry pi serial number
	serial=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`
fi


# Check if site is up every 5 minutes else restart forwarding service
while true; do

	# Check if we can connect outbound (and DNS works)
    ping -c 1 mit.edu > /dev/null 2>&1
	if [ "$?" -eq 0 ]
	then
		echo 'Network is up.'	
	else
		echo 'Network is down, restarting connman.'	
        sudo service connman restart > /dev/null 2>&1
    fi

	# Check if serveo is up
	wget --server-response --spider $url > /dev/null 2>&1
	if [ "$?" -eq 0 ]
	then
		echo 'Site is up'	
	else
		echo 'Site is down, restarting'

		# TODO: Check if brain is running, else...send an error somewhere

		sudo killall -s 9 autossh > /dev/null 2>&1
		autossh -M 0 -R $url:80:localhost:80 serveo.net -R $serial:22:localhost:22 serveo.net -oServerAliveInterval=30 -oStrictHostKeyChecking=no -f
	fi

	# Update every 5 minutes
	sleep 300
	
done
