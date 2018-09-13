#!/bin/bash

# Get the path to THIS script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Have we setup the local python environment we need?
if ! [ -d $DIR/venv ]; then
    echo 'Error: please run: ./scripts/setup_python.sh
Exiting.'
    exit 1
fi

# If there is a current python virtual environment, deactivate it.
if ! [ -z "${VIRTUAL_ENV}" ] ; then
    deactivate
fi

# Activate the python env for this bash process
source $DIR/venv/bin/activate

# Pass all these to django as env vars.
export IOT_PRIVATE_KEY=$DIR/registration/data/rsa_private.pem
export CA_CERTS=$DIR/registration/data/roots.pem
export GCLOUD_PROJECT=openag-v1
export GCLOUD_REGION=us-central1
export GCLOUD_DEV_REG=device-registry


# Load the DEVICE_ID environment variable created by the above script.
DEVICE_ID_FILE=$DIR/registration/data/device_id.bash
if [ -f $DEVICE_ID_FILE ]; then
    source $DEVICE_ID_FILE
fi


# Turn on debug logging if we are in developer mode
if [ -f $TOPDIR/config/develop ]; then
    export OPENAG_LOG_LEVEL=DEBUG
fi


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

# Export command line arguments
export NO_DEVICE
export SIMULATE

# Run app
python3.6 manage.py runserver 0.0.0.0:80

