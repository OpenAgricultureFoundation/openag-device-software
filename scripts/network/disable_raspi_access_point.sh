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
sudo cp $PROJECT_ROOT/scripts/network/raspi-network-configs/dhcpcd.conf.noap /etc/dhcpcd.conf

# Restart dhcp service
sudo service dhcpcd restart
