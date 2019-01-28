#! /bin/bash

# Get command line args
if [ $# -eq 0 ]; then
    echo "Please provide the following command line arguments:"
    echo "  wifi ssid (e.g. ElectricElephant)"
    echo "  wifi password (e.g. mysecretpasword)"
    exit 1
fi
if [ $# -eq 1 ]; then
    echo "Please provide the password for the wifi you want to connect to (or '' for no password.)"
    exit 1
fi

# Set wifi credentials
SSID=$1
PASSWORD=$2

# Append network config to wpa supplicant config file
NETWORK_STRING=$'\n'"network={"$'\n\t'"ssid="$'"'"${SSID}"$'"'$'\n\t'"psk="$'"'"${PASSWORD}"$'"'$'\n'"}"$'\n'
sudo echo "${NETWORK_STRING}" >> /etc/wpa_supplicant/wpa_supplicant.conf

# Disable wifi access point
echo "Disabling access point..."
bash $PROJECT_ROOT/scripts/network/disable_raspi_access_point.sh
sleep 3

# Restart wifi connection
echo "Restarting wifi connection..."
wpa_cli -i wlan0 reconfigure
sleep 3
