#! /bin/bash

# Update and install tools
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install dnsmasq -y
sudo apt-get install hostapd -y

# Make sure platform info is sourced
if [[ -z "$PLATFORM" ]]; then
	source get_platform_info.sh > /dev/null 2>&1
fi

# Create hostapd.conf with custom access point name
cd raspi-network-configs
cp hostapd.conf.template hostapd.conf
echo "ssid=$WIFI_ACCESS_POINT" >> hostapd.conf

# Configure access point host software
cp hostapd.conf /etc/hostapd/hostapd.conf
cp hostapd /etc/default/hostapd

# Configure dhcp server
cp dnsmasq.conf /etc/dnsmasq.conf

# Allow user to access wpa conf w/out being root
sudo chown -R $USER:$USER /etc/wpa_supplicant/
