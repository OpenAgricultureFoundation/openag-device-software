#!/bin/sh
 
echo "Using sudo to configure your networking, please enter your password:"
sudo service connman stop
sleep 5
sudo rm -fr /var/lib/connman/*.config /var/lib/connman/wifi_*
sudo service connman start
 
