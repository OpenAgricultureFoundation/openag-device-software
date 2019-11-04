#!/bin/bash

# For use on devices with an I2C bus built in: beaglebone, Pi

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

i2cdetect -y -r $DEFAULT_I2C_BUS
