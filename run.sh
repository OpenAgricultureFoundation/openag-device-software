#!/bin/bash

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
python3 manage.py runserver