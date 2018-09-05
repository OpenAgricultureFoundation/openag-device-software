#!/bin/bash

serial=`sudo hexdump -e '8/1 "%c"' "/sys/bus/i2c/devices/0-0050/eeprom" -s 16 -n 12 2>&1`
echo $serial
