#! /bin/bash

# Note: Use this by running source get_platform_info.sh
# Then getting environment variables e.g. in python: os.getenv("VAR_NAME")

# Initialize platform info
SERIAL_NUMBER=unknown
WIFI_ACCESS_POINT=unknown
IS_WIFI_ENABLED=0

# Check for beaglebone black
if [ -f /etc/dogtag ]; then
    DOGTAG=`cat /etc/dogtag`
    if [[ $DOGTAG == *"Beagle"* ]]; then
     
      # Check for beaglebone black wireless
      WLAN=`ifconfig wlan0`
      if [[ $WLAN == *"wlan0: flags"* ]]; then
      	PLATFORM=beaglebone-black-wireless
      	SERIAL_NUMBER=`sudo hexdump -e '8/1 "%c"' /sys/bus/i2c/devices/0-0050/eeprom -s 16 -n 12`
      	WIFI_ACCESS_POINT=`cat /tmp/hostapd-wl18xx.conf | grep "^ssid" | cut -d '=' -f 2`
        IS_WIFI_ENABLED=true
      else
      	PLATFORM=beaglebone-black-wired
      	SERIAL_NUMBER=`sudo hexdump -e '8/1 "%c"' /sys/bus/i2c/devices/0-0050/eeprom -s 16 -n 12`
        IS_WIFI_ENABLED=false
      fi

    fi
fi

# Check for raspberry pi
CPUINFO=`cat /proc/cpuinfo`
if [[ $CPUINFO == *"BCM2708"* ]]; then
	PLATFORM=raspberry-pi-1
	SERIAL_NUMBER=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`
  IS_WIFI_ENABLED=false
elif [[ $CPUINFO == *"BCM2709"* ]]; then
	PLATFORM=raspberry-pi-2
	SERIAL_NUMBER=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`
  IS_WIFI_ENABLED=false
elif [[ $CPUINFO == *"BCM2835"* ]]; then
	PLATFORM=raspberry-pi-3
	SERIAL_NUMBER=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2`
  IS_WIFI_ENABLED=false
fi

# Set remote device ui url
if [[ ! $SERIAL_NUMBER == "unknown" ]]; then
  REMOTE_DEVICE_UI_URL=openag-$SERIAL_NUMBER.serveo.net
else
  REMOTE_DEVICE_UI_URL=unknown
fi

# Export platform information
export PLATFORM="$PLATFORM"
export SERIAL_NUMBER="$SERIAL_NUMBER"
export WIFI_ACCESS_POINT="$WIFI_ACCESS_POINT"
export REMOTE_DEVICE_UI_URL="$REMOTE_DEVICE_UI_URL"
export IS_WIFI_ENABLED="$IS_WIFI_ENABLED"

# Show platform information
printf "\nGetting platform info...\n\n"
echo PLATFORM: $PLATFORM
echo SERIAL_NUMBER: $SERIAL_NUMBER
echo WIFI_ACCESS_POINT: $WIFI_ACCESS_POINT
echo REMOTE_DEVICE_UI_URL: $REMOTE_DEVICE_UI_URL
echo IS_WIFI_ENABLED: $IS_WIFI_ENABLED
echo ""
