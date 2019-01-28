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
	 
touch "/var/lib/connman/$SSID.config.tmp"
chmod 777 "/var/lib/connman/$SSID.config.tmp"
echo "[service_$1]
Type=wifi
Name=$SSID
Passphrase=$PASSWORD
"> "/var/lib/connman/$SSID.config.tmp"
mv "/var/lib/connman/$SSID.config.tmp" "/var/lib/connman/$SSID.config"
sleep 3
sudo service connman restart
sleep 3
