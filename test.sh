#!/bin/bash

printf "\n~~~ Running tests...this can take a few minutes ~~~\n"

# Get project root
PROJECT_ROOT=`pwd`

# Activate virtual 
source $PROJECT_ROOT/venv/bin/activate

# Run our code formatter
printf "\nRunning code formatter...\n"
black app/ device/

# Run static type checks, TODO: run for all codebase
printf "\nRunning static type checks...\n"
mypy --config-file mypy.ini device app

if [[ $? != 0 ]]; then
    echo "Error: please fix the above type checks and re-run script"
    exit 1
else
	printf "...type checks complete!\n"
fi

printf "\nRunning unit tests...\n"
python -m pytest $PROJECT_ROOT --cov device app
