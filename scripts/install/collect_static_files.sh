#!/bin/bash

# Log collection status
echo "Collecting static files..."

# Check virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]] ; then
    echo "Please activate your virtual environment then re-run script"
    exit 1
fi

# Collect static files
python3.6 manage.py collectstatic --clear --link --noinput
