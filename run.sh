#!/bin/bash

# Get project root, assumes this script is in project root
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Source virtual environment
source $PROJECT_ROOT/venv/bin/activate

# Only if we are on linux, we run a light weight web server to vend images
if [[ "$OSTYPE" == "linux"* ]]; then
    sudo pkill busybox
    sudo busybox httpd -p 8088 -h $PROJECT_ROOT/data/images/ 
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
    --no-device)           shift               
                                NO_DEVICE="true"
                                ;;
    --simulate)           shift               
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
