#! /bin/bash

# Ensure virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]] ; then
    echo "Please activate your virtual environment then re-run script"
    exit 1
fi

# Stop network routing processes
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Reconfigure dhcp config
sudo cp $PROJECT_ROOT/scripts/network/raspi-network-configs/dhcpcd.conf.ap /etc/dhcpcd.conf

# Restart dhcp config
sudo service dhcpcd restart

# Restart network routing processes
sudo systemctl start hostapd
sudo systemctl start dnsmasq
