#!/bin/bash

# Ensure virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]] ; then
    echo "Please activate your virtual environment then re-run script"
    exit 1
fi

# Requre platform to be a beaglebone
if [[ $PLATFORM != *"beaglebone"* ]]; then
	echo "Advanced wifi not supported for non-beaglebone platforms"
	exit 1
fi

# Check for command line args
if [ $# -lt 7 ]; then
    echo "Please provide the following command line arguments:"
    echo "  ssid_name passphrase hidden_ssid security eap identity phase2"
    exit 1
fi

# Get command line args
ssid_name=$1
passphrase=$2
hidden_ssid=$3
security=$4
eap=$5
identity=$6
phase2=$7

# Build up the config file contents
contents="[service_wifi_openag]
Type=wifi
Name=$ssid_name
Hidden=$hidden_ssid"
 
if [ $security != "none" ]; then
    contents+="
Security=$security"
fi

# Passphrase / password is optional, use if the string is not zero length.
if [ 0 -ne ${#passphrase} ]; then
    contents+="
Passphrase=$passphrase"
fi

# Only if security is WPA-EAP (ieee8021x) then we add the last 3 fields
if [ $security == "ieee8021x" ]; then
    contents+="
EAP=$eap
Identity=$identity
Phase2=$phase2"
fi

touch "/var/lib/connman/openag.config.tmp"
chmod 777 "/var/lib/connman/openag.config.tmp"
echo "$contents"> "/var/lib/connman/openag.config.tmp"
mv "/var/lib/connman/openag.config.tmp" "/var/lib/connman/openag.config"
sleep 30
 
echo "Using sudo to configure your networking, please enter your password:"
sudo service connman restart

# Wait for network to restart
sleep 30

# Enable remote access
bash $PROJECT_ROOT/scripts/network/enable_remote_access.sh $REMOTE_DEVICE_UI_URL 
