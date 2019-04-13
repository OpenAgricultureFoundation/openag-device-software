#!/bin/bash

# Check valid command line arguments
if [ $# -lt 2 ]; then
    echo $#
    echo "Please provide the following command line arguments:"
    echo "  PROJECT_ROOT (e.g. /home/pi/openag-device-software)"
    echo "  FILE (e.g. 2019-04-01_T15-58-19Z_Camera-Top.png)"
    exit 1
fi

# Initialize passed in arguments
PROJECT_ROOT=$1
FILE=$2

# Load the device id file if it exists
DEVICE_ID="not-set-yet"
DEVICE_ID_FILE=$PROJECT_ROOT/data/registration/device_id.bash
if [[ -f $DEVICE_ID_FILE ]]; then
    source $DEVICE_ID_FILE
fi

# Command line POST of test image to local server:
# Can only send one extra field in the multi-part form upload,
# so we override the filename field with the device id + file name.
FILE_NAME=$DEVICE_ID'_'$FILE
DATA='data=@'$FILE';filename='$FILE_NAME
RET=`curl http://localhost:5000/fb-func-test/us-central1/saveImage -F "$DATA" `

#debugrob: test this with the curl available in the balena docker image on a ras pi zero


if [[ $RET = *"error"* ]]; then
  echo "Error: could not send the file: $FILE"
  echo $RET
  exit 1
fi


