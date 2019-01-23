#!/bin/bash

# Initialize passed in variables
PROJECT_ROOT=$1

# TODO: Make sure we received project root as passed in parameter

# Set project root as environment variable in virtual environment
printf "\n# Set project root\n" >> $PROJECT_ROOT/venv/bin/activate
echo "export PROJECT_ROOT=$PROJECT_ROOT" >> $PROJECT_ROOT/venv/bin/activate

# Set platform environment variables in virtual environment
printf "\n# Set platform variables\n" >> $PROJECT_ROOT/venv/bin/activate
echo "source $PROJECT_ROOT/scripts/platform/get_platform_info.sh" >> $PROJECT_ROOT/venv/bin/activate
