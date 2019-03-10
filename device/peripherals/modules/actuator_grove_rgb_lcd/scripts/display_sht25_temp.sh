#!/bin/bash

# Read the SHT25 temp and humidity and display it on:
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

# converts an ASCII char to its decimal value and puts it in $ORDR
function ord { 
    printf -v ORDR "%d" "'$1"
}

# CNS board uses mux channel zero
MUX=0
i2cset -y $DEFAULT_I2C_BUS $DEFAULT_MUX_ADDRESS $((1<<$MUX))

# Trigger (wake it up) SHT25 temp measurement (no hold master)
i2cset -y $DEFAULT_I2C_BUS 0x40 0xF3

# Wait for sensor to process
sleep 0.1

# Get raw bytes from SHT25
msb=`i2cget -y $DEFAULT_I2C_BUS 0x40`
lsb=`i2cget -y $DEFAULT_I2C_BUS 0x40`

# Convert msb & lsb to decimal
msb=$(($msb&0xff))
lsb=$(($lsb&0xff))

# Calculate temperature signal
val=256
temperature_signal=`echo $msb*$val + $lsb | bc`

# Calculate temperature in C and F
b=46.85
m=175.72
d=65536
g=1.8
o=32
temperature_c=`echo $m*$temperature_signal/$d - $b | bc`
temperature_f=`echo $temperature_c*$g + $o | bc`
temp=`printf "%sC / %sF" $temperature_c $temperature_f`
echo $temp

# SHT25 humidity measurement 
i2cset -y $DEFAULT_I2C_BUS 0x40 0xF5
sleep 0.29 # sleep 29ms
msb=`i2cget -y $DEFAULT_I2C_BUS 0x40` # Get raw bytes from SHT25
lsb=`i2cget -y $DEFAULT_I2C_BUS 0x40`
msb=$(($msb&0xff)) # Convert msb & lsb to decimal
lsb=$(($lsb&0xff))
# Calculate humidity signal
val=256
raw=`echo $msb*$val + $lsb | bc`
a=-6.0
b=125.0
humidity=`echo $a+\(\($raw*$b\)/$d\) | bc`
hum="$humidity %RH"
echo $hum

# LCD has two I2C addresses
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

# write the temp string one char at a time
CHAR=0x40
for (( i=0; i<${#temp}; i++ )); do
  ord "${temp:$i:1}" 
  i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CHAR $ORDR
done

# 16 chars per line limit, this is a newline
i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CMD 0xC0 # command: new line

# write the humidity string one char at a time
for (( i=0; i<${#hum}; i++ )); do
  ord "${hum:$i:1}" 
  i2cset -y $DEFAULT_I2C_BUS $DISPLAY_TEXT_ADDR $CHAR $ORDR
done

