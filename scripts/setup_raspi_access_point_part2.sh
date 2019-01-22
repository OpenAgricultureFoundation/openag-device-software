#! /bin/bash

# Configure static ip
NETWORK_STRING=$'\n'"interface wlan0"$'\n\t'"ip_address=192.168.8.1/24"$'\n\t'"nohook wpa_supplicant"$'\n'
sudo echo "${NETWORK_STRING}" >> /etc/dhcpcd.conf

# Restart dhcpd
sudo service dhcpcd restart
