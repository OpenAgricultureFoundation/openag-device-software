#!/bin/sh

# Trigger co2 measurement
i2cset -y 2 0x15 0x04 0x13 0x8b 0x00 0x01 i

# Wait for sensor to process
sleep 0.1

# Get raw bytes
xx=`i2cget -y 2 0x15`
xx=`i2cget -y 2 0x15`
msb=`i2cget -y 2 0x15`
lsb=`i2cget -y 2 0x15`

# Convert msb & lsb to decimal
msb=$(($msb&0xff))
lsb=$(($lsb&0xff))

# Calculate temperature signal
val=256
co2=`echo $msb*$val + $lsb | bc`
echo $co2 ppm