#!/bin/bash

# Get the path to THIS script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Have we setup the local python environment we need?
if ! [ -d $DIR/venv ]; then
    echo 'Error: please run: ./setup_python.sh
Exiting.'
    exit 1
fi

# If there is a current python virtual environment, deactivate it.
if ! [ -z "${VIRTUAL_ENV}" ] ; then
    deactivate
fi

# Activate the python env for this bash process
source $DIR/venv/bin/activate

# Does the data dir exist? If not, then create it.
if [ ! -d $DIR/registration/data ]; then
    mkdir -p $DIR/registration/data
fi

# Automatically generate keys the first time we are run.  Saved to data dir.
IOT_PRIVATE_KEY=$DIR/registration/data/rsa_private.pem
if [ ! -f $IOT_PRIVATE_KEY ]; then
    # automatically create our keys the first time
    echo "Registering this device..."
    $DIR/registration/one_time_key_creation_and_iot_device_registration.sh $DIR/registration/data
fi

# If we need to use the UI to register the device, tell the user and exit.
V_CODE=$DIR/registration/data/verification_code.txt
if [ -f $V_CODE ]; then
    cat $V_CODE
    rm $V_CODE
    echo "Exiting.  Please use the UI to register this device with the above code, then rerun this script."
    exit 0
fi

# Pass all these to django as env vars.
export IOT_PRIVATE_KEY
export CA_CERTS=$DIR/registration/data/roots.pem
export GCLOUD_PROJECT=openag-v1
export GCLOUD_REGION=us-central1
export GCLOUD_DEV_REG=device-registry


# Load the DEVICE_ID environment variable created by the above script.
DEVICE_ID_FILE=$DIR/registration/data/device_id.bash
if [ ! -f $DEVICE_ID_FILE ]; then
    echo "Error: This device is not registered with the backend."
    exit 1
fi
source $DEVICE_ID_FILE


# Initialize command line arg default values
NO_DEVICE="false"
SIMULATE="false"

# Get command line arguments
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -nd | --no-device)           shift               
                                NO_DEVICE="true"
                                ;;
    -nd | --simulate)           shift               
                                SIMULATE="true"
                                ;;
    *) 
    POSITIONAL+=("$1")
    shift
    ;;
esac
done
set -- "${POSITIONAL[@]}" 

# Check if about.json if configured
if grep "<DEVICE>-<VERSION>-<ID>" about.json > /dev/null; then
    echo "Device about.json is not configured, running with --no-device option"
    NO_DEVICE="true"
fi

# Export command line arguments
export NO_DEVICE
export SIMULATE

# Run app
python3 manage.py runserver 0.0.0.0:80

