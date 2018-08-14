#!/bin/sh
 
connmanctl disable wifi > /dev/null 2>&1
sleep 1
echo "Using sudo to configure your networking, please enter your password:"
sudo rm -fr /var/lib/connman/*.config /var/lib/connman/wifi_*
sleep 1
connmanctl enable wifi > /dev/null 2>&1
 
