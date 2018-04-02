#!/bin/bash

# Initialize command line arg default values
NO_DEVICE="false"

# Get command line arguments
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --nodevice)
    NO_DEVICE="true"
    shift # past argument
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

# Export command line arguments
export NO_DEVICE

# Run app
python manage.py runserver