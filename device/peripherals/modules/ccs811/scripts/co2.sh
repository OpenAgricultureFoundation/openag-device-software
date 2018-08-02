echo Resetting sensor...
i2cset -y 2 0x5a 0xFF 0x11 0xE5 0x72 0x8A i


echo Starting app...
i2cset -y 2 0x5a 0xF4


echo Reading status...
i2cget -y 2 0x5a 0x00

# echo Reading error...
# i2cget -y 2 0x5a 0x0E

# echo Reading status...
# i2cget -y 2 0x5a 0x00


echo Setting measurement mode...
i2cset -y 2 0x5a 0x01 0x10

sleep 3

echo Reading status...
i2cget -y 2 0x5a 0x00

# echo Reading error...
# i2cget -y 2 0x5a 0x0E