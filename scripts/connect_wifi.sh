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
sleep 2
connmanctl config $1 --autoconnect yes > /dev/null 2>&1
connmanctl disable wifi > /dev/null 2>&1
sleep 1
connmanctl enable wifi > /dev/null 2>&1

# We must restart autossh, otherwise serveo.net won't let us back in.
sleep 4
sudo killall -s 9 autossh > /dev/null 2>&1
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
python $DIR/forward_ports.py > /dev/null 2>&1
 
#connmanctl services
#ifconfig wlan0
