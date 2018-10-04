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
SSID=`connmanctl services $1 | grep "Name =" | cut --delimiter=' ' --fields 5-10`
SSIDLEN=`echo -n $SSID | wc -m`
if [ $SSIDLEN -eq 0 ]; then
    echo "Can't connect to a wifi with a hidden SSID, sorry.  Use connmanctl"
    exit 1
fi
 
touch "/var/lib/connman/$SSID.config.tmp"
chmod 777 "/var/lib/connman/$SSID.config.tmp"
echo "[service_$1]
Type=wifi
Name=$SSID
Passphrase=$2
"> "/var/lib/connman/$SSID.config.tmp"
mv "/var/lib/connman/$SSID.config.tmp" "/var/lib/connman/$SSID.config"
sleep 2
 
echo "Using sudo to configure your networking, please enter your password:"
sudo service connman restart

# We must restart autossh, otherwise serveo.net won't let us back in.
sleep 4
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
$DIR/forward_ports.sh
 
