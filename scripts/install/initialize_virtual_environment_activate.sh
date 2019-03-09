#!/bin/bash

# Log initialization status
echo "Initializing virtual environment activate script..."

# Check valid command line arguments
if [[ $# -eq 0 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  PROJECT_ROOT (e.g. /home/pi/openag-device-software)"
    echo "  LOG_LEVEL (e.g. DEBUG, INFO, WARNING, ERROR, or CRITICAL)"
    echo "  RUNTIME_MODE (e.g. PRODUCTION or DEVELOPMENT)"
    exit 1
elif [[ $# -eq 1 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  LOG_LEVEL (e.g. DEBUG, INFO, WARNING, ERROR, or CRITICAL)"
    echo "  RUNTIME_MODE (e.g. PRODUCTION or DEVELOPMENT)"
    exit 1
elif [[ $# -eq 2 ]]; then
    echo "Please provide the following command line arguments:"
    echo "  RUNTIME_MODE (e.g. PRODUCTION or DEVELOPMENT)"
    exit 1
fi

# Initialize passed in arguments
PROJECT_ROOT=$1
LOG_LEVEL=$2
RUNTIME_MODE=$3

# Check virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
  echo "Unable to initialize virtual environment, venv directory does not exist"
  exit 1
fi

# Set project root as environment variable in virtual environment
printf "\n# Set project root\n" >> $PROJECT_ROOT/venv/bin/activate
echo "export PROJECT_ROOT=$PROJECT_ROOT" >> $PROJECT_ROOT/venv/bin/activate

# Set log level in virtual environment
printf "\n# Set log level\n" >> $PROJECT_ROOT/venv/bin/activate
echo "export LOG_LEVEL=$LOG_LEVEL" >> $PROJECT_ROOT/venv/bin/activate

# Set runtime mode in virtual environment
printf "\n# Set runtime mode\n" >> $PROJECT_ROOT/venv/bin/activate
echo "export RUNTIME_MODE=$RUNTIME_MODE" >> $PROJECT_ROOT/venv/bin/activate

# Set platform environment variables in virtual environment
printf "\n# Source project activate file\n" >> $PROJECT_ROOT/venv/bin/activate
echo "source $PROJECT_ROOT/scripts/install/activate.sh" >> $PROJECT_ROOT/venv/bin/activate

exit 0
