#!/bin/sh
 
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
SSID=`connmanctl services $1 | grep "Name =" | cut --delimiter=' ' --fields 5-10`
 
echo "Using sudo to configure your networking, please enter your password:"
sudo touch "/var/lib/connman/$SSID.config"
sudo chmod 777 "/var/lib/connman/$SSID.config"
echo "[service_$1]
Type=wifi
Name=$SSID
Passphrase=$2
"> "/var/lib/connman/$SSID.config"
sleep 2
 
connmanctl connect $1
connmanctl config $1 --autoconnect yes
 
#connmanctl services
#ifconfig wlan0
