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

# Set all channels high
for i in `seq 0 7`;
do
  i2cset -y $DEFAULT_I2C_BUS 0x47 $((0x30+$i)) 0xff 0x00 i
done