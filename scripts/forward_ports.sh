#! /bin/bash

printf "\nForwarding ports...\n\n"

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
wget --server-response --spider $REMOTE_DEVICE_UI_URL -T 3 -t 2 > /dev/null 2>&1
if [ "$?" -eq 0 ]
then
	echo 'Site is up'	
else
	echo 'Site is down, restarting'

	# TODO: Check if brain is running, else...send an error somewhere

	sudo killall -s 9 autossh > /dev/null 2>&1
	autossh -M 0 -R openag-$SERIAL_NUMBER:80:localhost:8000 serveo.net -R $SERIAL_NUMBER:22:localhost:22 serveo.net -oServerAliveInterval=30 -oStrictHostKeyChecking=no -f
fi
