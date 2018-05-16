#!/bin/sh

# Trigger temp measurement (no hold master)
i2cset -y 2 0x40 0xe7

# Wait for sensor to process
sleep 0.1

# get status byte
byte=`i2cget -y 2 0x40`
echo $byte
