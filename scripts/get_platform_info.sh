#! /bin/bash

# Note: Use this by running source get_platform_info.sh
# Then getting environment variables e.g. in python: os.getenv("VAR_NAME")

# Initialize platform info
SERIAL_NUMBER=unknown
WIFI_ACCESS_POINT=unknown
IS_WIFI_ENABLED=false
IS_I2C_ENABLED=false
DEFAULT_I2C_BUS=none

# Check for beaglebone black
if [ -f /etc/dogtag ]; then
    DOGTAG=`cat /etc/dogtag`
    if [[ $DOGTAG == *"Beagle"* ]]; then
     
      # Check for beaglebone black wireless
      WLAN=`ifconfig wlan0`
      if [[ $WLAN == *"wlan0: flags"* ]]; then
      	PLATFORM=beaglebone-black-wireless
        IS_WIFI_ENABLED=true
        WIFI_ACCESS_POINT=`cat /tmp/hostapd-wl18xx.conf | grep "^ssid" | cut -d '=' -f 2`
      else
      	PLATFORM=beaglebone-black-wired
        IS_WIFI_ENABLED=false
      fi

      # Set general beaglebone info
      SERIAL_NUMBER=`sudo hexdump -e '8/1 "%c"' /sys/bus/i2c/devices/0-0050/eeprom -s 16 -n 12`
      IS_I2C_ENABLED=true
      DEFAULT_I2C_BUS=2

    fi
fi

# Check for raspberry pi
CPUINFO=`cat /proc/cpuinfo`
if [[ $CPUINFO == *"BCM2708"* ]]; then
	PLATFORM=raspberry-pi-1
elif [[ $CPUINFO == *"BCM2709"* ]]; then
	PLATFORM=raspberry-pi-2
elif [[ $CPUINFO == *"BCM2835"* ]]; then
	PLATFORM=raspberry-pi-3
fi

# Set general raspberry pi info
if [[ $PLATFORM == *"raspberry-pi"* ]]; then
  SERIAL_NUMBER=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`
  IS_WIFI_ENABLED=true
  IS_I2C_ENABLED=true
  DEFAULT_I2C_BUS=1
fi


# Check if platform is a linux machine
# TODO: This is a bit unclear, but might be fine for awhile
# The uses cases this is build for is a development machine that runs ubuntu 16.04
# And a fanless PC that runs the hazelnut computer that runs ubuntu 18.04
if [[ $PLATFORM == "unknown" && $OSTYPE == "linux"* ]]; then
  PLATFORM=linux-machine
  IS_WIFI_ENABLED=true
  SERIAL_NUMBER=`sudo dmidecode -t system | grep Serial | cut -d ' ' -f 3`
  IS_I2C_ENABLED=false
fi

# Check if platform is an osx machine
if [[ $PLATFORM == "unknown" && $OSTYPE == "darwin"* ]]; then
  PLATFORM=osx-machine
  IS_WIFI_ENABLED=true
  SERIAL_NUMBER=unknown-but-easily-knowable-if-you-edit-me
  IS_I2C_ENABLED=false
fi

# Set remote device ui url
if [[ ! $SERIAL_NUMBER == "unknown" ]]; then
  REMOTE_DEVICE_UI_URL=openag-$SERIAL_NUMBER.serveo.net
else
  REMOTE_DEVICE_UI_URL=unknown
fi

# Export platform information
export PLATFORM=$PLATFORM
export SERIAL_NUMBER=$SERIAL_NUMBER
export WIFI_ACCESS_POINT=$WIFI_ACCESS_POINT
export REMOTE_DEVICE_UI_URL=$REMOTE_DEVICE_UI_URL
export IS_WIFI_ENABLED=$IS_WIFI_ENABLED
export IS_I2C_ENABLED=$IS_I2C_ENABLED
export DEFAULT_I2C_BUS=$DEFAULT_I2C_BUS

# Show platform information
printf "\nGetting platform info...\n\n"
echo PLATFORM: $PLATFORM
echo SERIAL_NUMBER: $SERIAL_NUMBER
echo WIFI_ACCESS_POINT: $WIFI_ACCESS_POINT
echo REMOTE_DEVICE_UI_URL: $REMOTE_DEVICE_UI_URL
echo IS_WIFI_ENABLED: $IS_WIFI_ENABLED
echo IS_I2C_ENABLED: $IS_I2C_ENABLED
echo DEFAULT_I2C_BUS: $DEFAULT_I2C_BUS
echo ""
