#!/bin/bash

# Initialize command line args
DEVELOPMENT="FALSE"
PRODUCTION="FALSE"

# Collect command line args
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --development)
    DEVELOPMENT="TRUE"
    shift # past argument
    ;;
    --production)
    PRODUCTION="TRUE"
    shift # past argument
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

# Get runtime environment
echo "Getting runtime mode..."
if [[ ("$DEVELOPMENT" == "TRUE") && ("$PRODUCTION" == "FALSE") ]]; then
	RUNTIME_MODE="DEVELOPMENT"
	LOG_LEVEL="DEBUG"
elif [[ ("$DEVELOPMENT" == "FALSE") && ("$PRODUCTION" == "TRUE") ]]; then
	RUNTIME_MODE="PRODUCTION"
	LOG_LEVEL="INFO"
elif [[ ("$DEVELOPMENT" == "FALSE") && ("$PRODUCTION" == "FALSE") ]]; then
	echo "Please specify the runtime environment with --development or --production"
	exit 1
else
	echo "Please specify either --development or --production"
	exit 1
fi
echo RUNTIME_MODE: $RUNTIME_MODE
echo LOG_LEVEL:  $LOG_LEVEL

# Get project root
echo "Getting project root..."
PROJECT_ROOT=`pwd`
echo PROJECT_ROOT: $PROJECT_ROOT

#debugrob, this causes us to fail since some of the scripts prompt for sudo
# Stop installation on any error
#set -e

# Just activate sudo here, so user doesn't have to install as root.
echo "Using sudo to update your system, please provide your password now:"
sudo date

# Clean up before doing a full install, only if on linux
if [[ "$OSTYPE" == "linux"* ]]; then
    sudo rm -fr $PROJECT_ROOT/venv
    sudo apt-get purge -y python3.6 
    sudo apt-get purge -y python3.5
    sudo apt-get purge -y python3 
fi

# Install software
echo "Installing software..."
bash $PROJECT_ROOT/scripts/install/initialize_device_config.sh $PROJECT_ROOT 
bash $PROJECT_ROOT/scripts/install/initialize_directory_structure.sh $PROJECT_ROOT
bash $PROJECT_ROOT/scripts/install/update_operating_system.sh
bash $PROJECT_ROOT/scripts/install/install_python36.sh
bash $PROJECT_ROOT/scripts/install/initialize_port80_forwarding.sh
bash $PROJECT_ROOT/scripts/install/install_misc_dependencies.sh
bash $PROJECT_ROOT/scripts/install/create_virtual_environment.sh $PROJECT_ROOT
bash $PROJECT_ROOT/scripts/install/initialize_virtual_environment_activate.sh $PROJECT_ROOT $LOG_LEVEL $RUNTIME_MODE
source $PROJECT_ROOT/venv/bin/activate
bash $PROJECT_ROOT/scripts/install/install_pygame.sh
bash $PROJECT_ROOT/scripts/install/install_python_requirements.sh
bash $PROJECT_ROOT/scripts/install/set_file_ownership.sh
bash $PROJECT_ROOT/scripts/install/install_network_utilities.sh
bash $PROJECT_ROOT/scripts/database/migrate_database.sh
bash $PROJECT_ROOT/scripts/database/create_project_users.sh
bash $PROJECT_ROOT/scripts/install/collect_static_files.sh
bash $PROJECT_ROOT/scripts/install/initialize_rc_local.sh $PROJECT_ROOT $RUNTIME_MODE $REMOTE_DEVICE_UI_URL $PLATFORM

# Installation complete
echo ""
echo "****************************************************************************************"
echo "*                             Installation complete!                                   *"
echo "****************************************************************************************"

# Log runtime specific usage instructions
if [[ "$RUNTIME_MODE" == "DEVELOPMENT" ]]; then
	echo "*                                                                                      *"
	echo "*  To run:                                                                             *"
	echo "*    Normal mode: ./run.sh                                                             *"
	echo "*    Simulation mode: ./simulate.sh                                                    *"
	echo "*                                                                                      *"
	echo "*  To acccess local ui:                                                                *"
	echo "*    Go to: http://localhost:8000/                                                     *"
fi

# Log general usage instructions
LINE="                                                                  *"
echo "*                                                                                      *"
echo "*  To access remote ui:                                                                *"
echo "*    Go to: https://$REMOTE_DEVICE_UI_URL ${LINE:${#REMOTE_DEVICE_UI_URL}}"
echo "*                                                                                      *"
echo "*  For documentation:                                                                  *"
echo "*    https://github.com/OpenAgInitiative/openag-device-software/blob/master/README.md  *"
echo "*                                                                                      *"
echo "****************************************************************************************"
echo "****************************************************************************************"
