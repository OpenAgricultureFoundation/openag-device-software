#!/bin/bash

# Get bbb serial number
serial=`sudo hexdump -e '8/1 "%c"' "/sys/bus/i2c/devices/0-0050/eeprom" -s 16 -n 12 2>&1`

# Kill all autossh ports
sudo killall -s 9 autossh > /dev/null 2>&1

# Forward ui via port 80 and ssh via port 22
autossh -M 0 -R $serial.serveo.net:80:localhost:80 serveo.net -R $serial:22:localhost:22 serveo.net -oServerAliveInterval=30 -oStrictHostKeyChecking=no -f
