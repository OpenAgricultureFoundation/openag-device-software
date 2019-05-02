#!/bin/bash

# Log getting status
printf "Getting iot settings...\n\n"


# Check valid command line arguments
if [ $# -eq 0 ]; then
    echo "Please provide the following command line arguments:"
    echo "  PROJECT_ROOT (e.g. /home/pi/openag-device-software)"
    exit 1
fi

# Initialize passed in arguments
PROJECT_ROOT=$1

# Get iot settings
export IOT_PRIVATE_KEY=$PROJECT_ROOT/data/registration/rsa_private.pem
export CA_CERTS=$PROJECT_ROOT/data/registration/roots.pem
export GCLOUD_PROJECT=openag-v1
export GCLOUD_REGION=us-central1
export GCLOUD_DEV_REG=device-registry

# Only for local testing/development.  You must have the MQTT service running
# on a test topic.  If so, manually set this environment var and run the brain.
# export IOT_TEST_TOPIC=events/test

# Load the device id file if it exists
DEVICE_ID_FILE=$PROJECT_ROOT/data/registration/device_id.bash
if [[ -f $DEVICE_ID_FILE ]]; then
    source $DEVICE_ID_FILE
else
	DEVICE_ID="not-set-yet"
fi


# Log results
echo IOT_PRIVATE_KEY: $IOT_PRIVATE_KEY
echo CA_CERTS: $CA_CERTS
echo GCLOUD_PROJECT: $GCLOUD_PROJECT
echo GCLOUD_REGION: $GCLOUD_REGION
echo GCLOUD_DEV_REG: $GCLOUD_DEV_REG
echo DEVICE_ID: $DEVICE_ID
echo ""
