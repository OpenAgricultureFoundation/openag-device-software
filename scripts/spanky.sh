#!/bin/bash
 
if [ $# -eq 0 ]; then
    echo "Please provide the following command line arguments:"
    echo "  wifi_<...> name you want to connect to,"
    echo "  password of the wifi you want to connect to."
    exit 1
fi
if [ $# -eq 1 ]; then
    echo "Please provide the password for the wifi you want to connect to (or '' for no password."
    exit 1
fi
 
# Get the SSID for this service
SSID="spanky"
 
echo "Using sudo to configure your networking, please enter your password:"
sudo touch "/var/lib/connman/$SSID.config"
sudo chmod 777 "/var/lib/connman/$SSID.config"
echo "[service_$1]
Type=wifi
Name=$SSID
SSID=7370616e6b79
Hidden=true
Passphrase=$2
"> "/var/lib/connman/$SSID.config"
sleep 2
 
connmanctl connect $1
sleep 1
connmanctl config $1 --autoconnect yes > /dev/null 2>&1
connmanctl disable wifi > /dev/null 2>&1
sleep 1
connmanctl enable wifi > /dev/null 2>&1
 
# Restart autossh
sleep 4
sudo killall -s 9 autossh > /dev/null 2>&1
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..
./forward_ports.sh > /dev/null 2>&1
 
#connmanctl services
#ifconfig wlan0
