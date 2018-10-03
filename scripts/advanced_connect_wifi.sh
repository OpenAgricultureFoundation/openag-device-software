#!/bin/bash
 
if [ $# -lt 7 ]; then
    echo "Please provide the following command line arguments:"
    echo "  ssid_name, passphrase, hiddenSSID, security, eap, identity, phase2"
    exit 1
fi

# Mandatory command line args in order
ssid_name=$1
passphrase=$2
hiddenSSID=$3
security=$4
eap=$5
identity=$6
phase2=$7

# Passphrase / password is optional
usingPass="Passphrase=$passphrase"
if [ $passphrase != "" ]; then
    usingPass=""
fi

# Only if security is WPA-EAP (ieee8021x) then we add the last 3 fields
usingEAP="EAP=$eap
Identity=$identity
Phase2=$phase2"
if [ $security != "ieee8021x" ]; then
    usingEAP=""
fi
 
echo "Using sudo to configure your networking, please enter your password:"
sudo touch "/var/lib/connman/openag.config"
sudo chmod 777 "/var/lib/connman/openag.config"
echo "[service_wifi_openag]
Type=wifi
Name=$ssid_name
Hidden=$hiddenSSID
Security=$security
$usingPass
$usingEAP
"> "/var/lib/connman/openag.config"
sleep 2
 
# We must restart autossh, otherwise serveo.net won't let us back in.
sleep 4
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
$DIR/forward_ports.sh
 
#connmanctl services
#ifconfig wlan0
