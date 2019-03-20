#!/bin/bash

# Grove RGB LCD v2.0 I2C board.
# http://wiki.seeedstudio.com/Grove-LCD_RGB_Backlight/

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

# converts an ASCII char to its decimal value and puts it in $ordr
function ord { 
    printf -v ordr "%d" "'$1"
}

# CNS board uses mux channel zero
MUX=0
i2cset -y $DEFAULT_I2C_BUS $DEFAULT_MUX_ADDRESS $((1<<$MUX))

# this device has two I2C addresses
DISPLAY_RGB_ADDR=0x62
DISPLAY_TEXT_ADDR=0x3e

# set backlight to (R,G,B) (values from 0..255 for each)
R=0x00
B=0x00
G=0xFF
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_RGB_ADDR 0 0
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_RGB_ADDR 1 0
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_RGB_ADDR 0x08 0xAA
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_RGB_ADDR 4 $R
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_RGB_ADDR 3 $G
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_RGB_ADDR 2 $B

# command: clear display
CMD=0x80
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CMD 0x01
sleep 0.05 # Wait for lcd to process

# command: display on, no cursor
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CMD $((0x08 | 0x04))
 
# command: 2 lines
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CMD 0x28
sleep 0.05 # Wait for lcd to process

# 16 chars per line limit
#i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CMD 0xC0 # command: new line

# write a string one char at a time
CHAR=0x40
ord "H"
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CHAR $ordr
ord "i"
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CHAR $ordr
ord " "
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CHAR $ordr
ord "B"
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CHAR $ordr
ord "r"
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CHAR $ordr
ord "i"
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CHAR $ordr
ord "d"
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CHAR $ordr
ord "g"
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CHAR $ordr
ord "e"
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CHAR $ordr
ord "t"
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CHAR $ordr
ord "!"
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CHAR $ordr



