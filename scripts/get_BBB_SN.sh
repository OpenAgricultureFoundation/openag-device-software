#!/bin/bash

SN=`sudo hexdump -e '8/1 "%c"' /sys/bus/i2c/devices/0-0050/eeprom -s 16 -n 12`
echo "$SN"
