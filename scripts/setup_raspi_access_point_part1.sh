#! /bin/bash

# Update and install tools
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install dnsmasq hostapd -y

# Stop new software
sudo systemctl stop dnsmasq
sudo systemctl stop hostapd

# Restart system
sudo reboot
