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

# Collect static files
python3.6 manage.py collectstatic
