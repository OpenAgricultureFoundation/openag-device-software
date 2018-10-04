#!/bin/bash

# Get the path to THIS script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# If there is a current python virtual environment, deactivate it.
if ! [ -z "${VIRTUAL_ENV}" ] ; then
    deactivate
fi

# Activate the python env for this bash process
source $DIR/venv/bin/activate

# Collect static files
cd ../
sudo venv/bin/python3.6 manage.py collectstatic