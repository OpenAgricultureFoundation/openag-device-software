#!/bin/bash

# Get project root, assumes this script is in project root
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Source virtual environment
source $PROJECT_ROOT/venv/bin/activate

# Turn on debug logging if we are in developer mode
if [ -f $PROJECT_ROOT/data/config/develop ]; then
    export OPENAG_LOG_LEVEL=DEBUG
fi

# Only if we are on linux, we run a light weight web server to vend images
if [[ "$OSTYPE" == "linux"* ]]; then
    sudo pkill busybox
    sudo busybox httpd -p 8080 -h $DIR/data/images/stored/
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
python3.6 manage.py runserver 0.0.0.0:8000

