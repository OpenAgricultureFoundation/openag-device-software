#!/bin/bash

# Publish probe start message
printf "Probing EDU 002\n"

# Probe tca9584 (mux)
printf "  Probing TCA9584..."
byte=`i2cget -y 2 0x77` 
if [[ "$byte" ]]; then 
	printf "PASSED\n"
	tca9584=1
fi

# Set mux to led panel
CHANNEL=3
i2cset -y 2 0x77 $((1<<$CHANNEL))

# Probe dac5578 (led controller)
printf "  Probing DAC5578..."
byte=`i2cget -y 2 0x47`
if [[ "$byte" ]]; then 
	printf "PASSED\n"
	dac5578=1

	# Turn off all lights
	i2cset -y 2 0x47 0x30 0xff 0x00 i
	i2cset -y 2 0x47 0x31 0xff 0x00 i
	i2cset -y 2 0x47 0x32 0xff 0x00 i
	i2cset -y 2 0x47 0x33 0xff 0x00 i
	i2cset -y 2 0x47 0x34 0xff 0x00 i
	i2cset -y 2 0x47 0x35 0xff 0x00 i
	i2cset -y 2 0x47 0x36 0xff 0x00 i
	i2cset -y 2 0x47 0x37 0xff 0x00 i
fi

# Set mux to air sensors
CHANNEL=2
i2cset -y 2 0x77 $((1<<$CHANNEL))

# Probe t6713 (co2 sensor, big)
printf "  Probing T6713..."
byte=`i2cget -y 2 0x15` 
if [[ "$byte" ]]; then 
	printf "PASSED\n"
	t6713=1
fi

# Probe ccs811 (co2 sensor, small)
printf "  Probing CCS811..."
byte=`i2cget -y 2 0x5a` 
if [[ "$byte" ]]; then 
	printf "PASSED\n"
	ccs811=1
fi

# Probe sht25 (temp / humidity sensor)
printf "  Probing SHT25..."
i2cset -y 2 0x40 0xf3 && sleep 0.1 && byte=`i2cget -y 2 0x40`
if [[ "$byte" ]]; then 
	printf "PASSED\n"
	sht25=1
fi

# Set mux to io expander
CHANNEL=5
i2cset -y 2 0x77 $((1<<$CHANNEL))

# Probe pfc8574 (io expander)
printf "  Probing PCF8574..."
byte=`i2cget -y 2 0x38`
if [[ "$byte" ]]; then 
	printf "PASSED\n"
	pcf8574=1
fi

# Assess overall probe
if [[ "$tca9584" ]] && [[ "$dac5578" ]] && [[ "$t6713" ]] && 
   [[ "$ccs811" ]] && [[ "$sht25" ]] && [[ "$pcf8574" ]]; then
	passed=1
	printf "Probe PASSED\n"
else
	printf "Probe FAILED\n"
fi

# Set mux to led panel
CHANNEL=3
i2cset -y 2 0x77 $((1<<$CHANNEL))

# Blink lights green x3 if passed
if [[ "$passed" ]]; then

	i2cset -y 2 0x47 0x35 0x00 0x00 i
	sleep .5

	i2cset -y 2 0x47 0x35 0xff 0x00 i
	sleep .5

	i2cset -y 2 0x47 0x35 0x00 0x00 i
	sleep .5

	i2cset -y 2 0x47 0x35 0xff 0x00 i
	sleep .5

	i2cset -y 2 0x47 0x35 0x00 0x00 i
	sleep .5

	i2cset -y 2 0x47 0x35 0xff 0x00 i
	sleep .5

# Blink lights red x3 if failed
else
	i2cset -y 2 0x47 0x32 0x00 0x00 i
	sleep .5

	i2cset -y 2 0x47 0x32 0xff 0x00 i
	sleep .5

	i2cset -y 2 0x47 0x32 0x00 0x00 i
	sleep .5

	i2cset -y 2 0x47 0x32 0xff 0x00 i
	sleep .5

	i2cset -y 2 0x47 0x32 0x00 0x00 i
	sleep .5

	i2cset -y 2 0x47 0x32 0xff 0x00 i
	sleep .5
fi


# If dac is good, cycle through lights
printf "\nCycling light channels...\n"

# Warm white light
echo "...Warm White"
i2cset -y 2 0x47 0x34 0x00 0x00 i
sleep 1
i2cset -y 2 0x47 0x34 0xff 0x00 i
sleep .5

# Cool white light
echo "...Cool White"
i2cset -y 2 0x47 0x36 0x00 0x00 i
sleep 1
i2cset -y 2 0x47 0x36 0xff 0x00 i
sleep .5

# Far red light
echo "...Far Red"
i2cset -y 2 0x47 0x30 0x00 0x00 i
sleep 1
i2cset -y 2 0x47 0x30 0xff 0x00 i
sleep .5

# Red light
echo "...Red"
i2cset -y 2 0x47 0x32 0x00 0x00 i
sleep 1
i2cset -y 2 0x47 0x32 0xff 0x00 i
sleep .5

# Green light
echo "...Green"
i2cset -y 2 0x47 0x35 0x00 0x00 i
sleep 1
i2cset -y 2 0x47 0x35 0xff 0x00 i
sleep .5

# Blue light
echo "...Blue"
i2cset -y 2 0x47 0x37 0x00 0x00 i
sleep 1
i2cset -y 2 0x47 0x37 0xff 0x00 i
sleep .5
