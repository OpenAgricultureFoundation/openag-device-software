#! /bin/bash

sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

sudo cp $OPENAG_BRAIN_ROOT/scripts/raspi-network-configs/dhcpcd.conf.ap /etc/dhcpcd.conf
sudo service dhcpcd restart

sudo systemctl start hostapd
sudo systemctl start dnsmasq
