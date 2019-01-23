#!/bin/bash

# Log install status
echo "Installing python requirements..."

# Check virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]] ; then
    echo "Please activate your virtual environment then re-run script"
    exit 1
fi

# Check project root exists
if [[ -z "$PROJECT_ROOT" ]]; then
	echo "Please set your project root in your virtual environment then re-run script"
    exit 1
fi

# Check pip3.6 is installed
INSTALL_PATH=`which pip3.6`
if [[ ! -f "$INSTALL_PATH" ]]; then
    echo "Please install pip3.6 then re-run script"
    exit 1
fi

# Install python requirements
pip3.6 download -d $PROJECT_ROOT/venv/pip_download -r $PROJECT_ROOT/requirements.txt
pip3.6 install -f $PROJECT_ROOT/venv/pip_download -r $PROJECT_ROOT/requirements.txt 
