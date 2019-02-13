#! /bin/bash

# Log install status
echo "Installing network utilities"

# Check virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]] ; then
    echo "Please activate your virtual environment then re-run script"
    exit 1
fi

# Check project root exists
if [[ -z "$PROJECT_ROOT" ]]; then
	echo "Please set your project root in your virtual environment then re-run script"
    exit 1
fi

# Install network utilites on linux operating system
if [[ "$OSTYPE" == "linux"* ]]; then
	sudo apt-get install autossh -y
	sudo apt-get install busybox -y

# Install network utilities on darwin operating system
elif [[ "$OSTYPE" == "darwin"* ]]; then
	brew install autossh

# Unsupported operating system
else
    echo "Unable to install network utils, unsupported operating system: $OSTYPE"
    exit 1
fi

# Install network utilites specific to raspberry pi platform
# We need these to toggle the wifi access point
if [[ "$OSTYPE" == "linux"* ]]; then
	sudo apt-get install dnsmasq -y
	sudo apt-get install hostapd -y
	cp $PROJECT_ROOT/scripts/network/raspi-network-configs/hostapd.conf.template $PROJECT_ROOT/scripts/network/raspi-network-configs/hostapd.conf
	echo "ssid=$WIFI_ACCESS_POINT" >> $PROJECT_ROOT/scripts/network/raspi-network-configs/hostapd.conf
	sudo cp $PROJECT_ROOT/scripts/network/raspi-network-configs/hostapd.conf /etc/hostapd/hostapd.conf
	sudo cp $PROJECT_ROOT/scripts/network/raspi-network-configs/hostapd /etc/default/hostapd
	sudo cp $PROJECT_ROOT/scripts/network/raspi-network-configs/dnsmasq.conf /etc/dnsmasq.conf
	sudo chown -R $USER:$USER /etc/wpa_supplicant/
fi
