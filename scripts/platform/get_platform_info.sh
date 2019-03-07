#! /bin/bash

# Note: Use this by running source get_platform_info.sh
# Then getting environment variables e.g. in python: os.getenv("VAR_NAME")

# Initialize platform info
PLATFORM=unknown
SERIAL_NUMBER=unknown
WIFI_ACCESS_POINT=unknown
IS_WIFI_ENABLED=false
IS_I2C_ENABLED=false
IS_USB_I2C_ENABLED=false
DEFAULT_I2C_BUS=none
DEFAULT_MUX_ADDRESS=0x77

# Check for beaglebone black
if [ -f /etc/dogtag ]; then
    DOGTAG=`cat /etc/dogtag`
    if [[ $DOGTAG == *"Beagle"* ]]; then
     
      # Check for beaglebone black wireless
      WLAN=`ifconfig | grep "wlan0:"`
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
      IS_USB_I2C_ENABLED=false

    fi
fi

# Check for raspberry pi
if [ -f '/proc/cpuinfo' ]; then
    CPUINFO=`cat /proc/cpuinfo`
    if [[ $CPUINFO == *"BCM2708"* ]]; then
        PLATFORM=raspberry-pi-1
    elif [[ $CPUINFO == *"BCM2709"* ]]; then
        PLATFORM=raspberry-pi-2
    elif [[ $CPUINFO == *"BCM2835"* ]]; then
        PLATFORM=raspberry-pi-3
    fi
fi

# Set general raspberry pi info
if [[ $PLATFORM == *"raspberry-pi"* ]]; then
  SERIAL_NUMBER=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2 | sed 's/^0*//' | awk '{print toupper($0)}'`
  WIFI_ACCESS_POINT=RaspberryPi-`echo $SERIAL_NUMBER | tail -c 5 | awk '{print toupper($0)}' `
  IS_WIFI_ENABLED=true
  IS_I2C_ENABLED=true
  DEFAULT_I2C_BUS=1
  IS_USB_I2C_ENABLED=false
fi


# Check if platform is a linux machine
# TODO: This is a bit unclear, but might be fine for a while
# The uses cases this is built for are: 
#  - A development machine that runs Ubuntu 16.04
#  - A fanless PC that runs the hazelnut computer and runs ubuntu 18.04
if [[ $PLATFORM == "unknown" && $OSTYPE == "linux"* ]]; then
  PLATFORM=linux-machine
  IS_WIFI_ENABLED=true
  SERIAL_NUMBER=`sudo dmidecode -t system | grep Serial | cut -d ' ' -f 3 `
  IS_I2C_ENABLED=false

  # Check if platform has a usb-to-i2c adapter cable
  if [[ `lsusb` == *"FT232"* ]]; then
    IS_USB_I2C_ENABLED=true
  else
    IS_USB_I2C_ENABLED=false
  fi
fi

# Check if platform is an osx machine
if [[ $PLATFORM == "unknown" && $OSTYPE == "darwin"* ]]; then
  PLATFORM=osx-machine
  IS_WIFI_ENABLED=true
  SERIAL_NUMBER=`system_profiler SPHardwareDataType | grep "Serial Number (system)" | awk '{print $4}'`
  IS_I2C_ENABLED=false

  # Check if platform has a usb-to-i2c adapter cable
  if [[ `system_profiler SPUSBDataType` == *"FTDI"* ]]; then
    IS_USB_I2C_ENABLED=true
  else
    IS_USB_I2C_ENABLED=false
  fi
fi

# Set remote device UI URL
if [[ ! $SERIAL_NUMBER == "unknown" ]]; then
  REMOTE_DEVICE_UI_URL=http://openag-$SERIAL_NUMBER.serveo.net
  # Serveo only works with lower case URLs
  REMOTE_DEVICE_UI_URL=`echo $REMOTE_DEVICE_UI_URL | awk '{print tolower($0)}'`
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
export IS_USB_I2C_ENABLED=$IS_USB_I2C_ENABLED
export DEFAULT_I2C_BUS=$DEFAULT_I2C_BUS
export DEFAULT_MUX_ADDRESS=$DEFAULT_MUX_ADDRESS

# Show platform information
printf "\nGetting platform info...\n\n"
echo PLATFORM: $PLATFORM
echo SERIAL_NUMBER: $SERIAL_NUMBER
echo WIFI_ACCESS_POINT: $WIFI_ACCESS_POINT
echo REMOTE_DEVICE_UI_URL: $REMOTE_DEVICE_UI_URL
echo IS_WIFI_ENABLED: $IS_WIFI_ENABLED
echo IS_I2C_ENABLED: $IS_I2C_ENABLED
echo IS_USB_I2C_ENABLED: $IS_USB_I2C_ENABLED
echo DEFAULT_I2C_BUS: $DEFAULT_I2C_BUS
echo DEFAULT_MUX_ADDRESS: $DEFAULT_MUX_ADDRESS
echo ""

