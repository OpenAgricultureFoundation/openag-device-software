#!/bin/bash

# Ensure virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]] ; then
    echo "Please activate your virtual environment then re-run script"
    exit 0
fi

# Ensure platform is i2c enabled
if [[ "$IS_I2C_ENABLED" != "true" ]]; then
	echo "Platform is not i2c enabled"
	exit 0
fi

# Trigger temp measurement (no hold master)
i2cset -y $DEFAULT_I2C_BUS 0x40 0xf3

# Wait for sensor to process
sleep 0.1

# Get raw bytes
msb=`i2cget -y $DEFAULT_I2C_BUS 0x40`
lsb=`i2cget -y $DEFAULT_I2C_BUS 0x40`
# checksum=`i2cget -y 2 0x40`
# echo $msb, $lsb, $checksum

# Convert msb & lsb to decimal
msb=$(($msb&0xff))
lsb=$(($lsb&0xff))
# echo $msb, $lsb

# Calculate temperature signal
val=256
temperature_signal=`echo $msb*$val + $lsb | bc`
# echo $temperature_signal

#Calculate temperature
b=46.85
m=175.72
d=65536
g=1.8
o=32
temperature_c=`echo $m*$temperature_signal/$d - $b | bc`
temperature_f=`echo $temperature_c*$g + $o | bc`
echo $temperature_c C
echo $temperature_f F