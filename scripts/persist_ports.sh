#!/bin/bash

# Check if site is up every 5 minutes else restart forwarding service
while true; do

	# Forward ports
	bash forward_ports.sh

	# Update every 5 minutes
	sleep 300
	
done
