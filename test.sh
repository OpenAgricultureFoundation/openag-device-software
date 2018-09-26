#!/bin/bash

printf "\n~~~ Running tests...this can take a few minutes ~~~\n"

# Get the path to THIS script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

# Have we setup the local python environment we need?
if ! [ -d $DIR/venv ]; then
    echo 'Error: please run: ./setup_python.sh
Exiting.'
    exit 1
fi

# If there is a current python virtual environment, deactivate it.
if ! [ -z "${VIRTUAL_ENV}" ] ; then
    source deactivate
fi

# Activate the python env for this bash process
source $DIR/venv/bin/activate

# Environment variables used in the IoT code, using CHECKED IN test device auth.
# export IOT_PRIVATE_KEY=$DIR/tests/data/rsa_private.pem
# export CA_CERTS=$DIR/tests/data/roots.pem
# export GCLOUD_PROJECT=openag-v1
# export GCLOUD_REGION=us-central1
# export GCLOUD_DEV_REG=device-registry
# source $DIR/tests/data/device_id.bash

# Run our code formatter
printf "\nRunning code formatter...\n"
black app/ device/

# Run static type checks, TODO: run for all codebase
# printf "\nRunning static type checks...\n"
# mypy --python-version 3.6 --follow-imports skip --ignore-missing-imports --strict --allow-untyped-decorators .
# printf "...type checks complete!\n"

printf "\nRunning unit tests...\n"
python -m pytest $DIR --cov device app
