#!/bin/bash

# Log install status
echo "Getting project root..."

# Get project root
CURRENT_DIRECTORY=`pwd`

# Check if running script from */openag-device-software
if [[ $CURRENT_DIRECTORY == *"openag-device-software" ]]; then
	PROJECT_ROOT=$CURRENT_DIRECTORY

# Check if running script from */openag-device-software/scripts
elif [[ $CURRENT_DIRECTORY == *"openag-device-software/scripts" ]]; then
	PROJECT_ROOT=${CURRENT_DIRECTORY%"/scripts"}

# Check if running script from */openag-device-software/scripts/install
elif [[ $CURRENT_DIRECTORY == *"openag-device-software/scripts/install" ]]; then
	PROJECT_ROOT=${CURRENT_DIRECTORY%"/scripts/install"}

# Check if running script from */openagbrain
elif [[ $CURRENT_DIRECTORY == *"openagbrain" ]]; then
	PROJECT_ROOT=$CURRENT_DIRECTORY

# Check if running script from */openagbrain/scripts
elif [[ $CURRENT_DIRECTORY == *"openagbrain/scripts" ]]; then
	PROJECT_ROOT=${CURRENT_DIRECTORY%"/scripts"}

# Check if running script from */openagbrain/scripts/install
elif [[ $CURRENT_DIRECTORY == *"openagbrain/scripts/install" ]]; then
	PROJECT_ROOT=${CURRENT_DIRECTORY%"/scripts/install"}

# Invalid run directory
	PROJECT_ROOT=unknown_project_root
	exit 1
fi

# Log project root
echo PROJECT_ROOT: $PROJECT_ROOT

# Move to project root
echo "Moving to project root..."
cd $PROJECT_ROOT

# Set device config file to unspecified
echo "unspecified" > $PROJECT_ROOT/data/config/device.txt

# Sym link rc.local to project rc.local
sudo rm -f /etc/rc.local
sudo ln -s $PROJECT_ROOT/data/config/rc.local.production /etc/rc.local

# TODO: Remove this: Initialize directory structure
sudo mkdir -p $PROJECT_ROOT/data/images/stored

# Install full system
echo "Installing full system..."
bash $PROJECT_ROOT/scripts/install/update_operating_system.sh
bash $PROJECT_ROOT/scripts/install/install_python36.sh
bash $PROJECT_ROOT/scripts/install/install_postgres.sh
bash $PROJECT_ROOT/scripts/install/initialize_port80_forwarding.sh
bash $PROJECT_ROOT/scripts/install/create_virtual_environment.sh $PROJECT_ROOT
bash $PROJECT_ROOT/scripts/install/initialize_virtual_environment_activate.sh $PROJECT_ROOT
source $PROJECT_ROOT/venv/bin/activate
bash $PROJECT_ROOT/scripts/install/install_cryptography_dependencies.sh
bash $PROJECT_ROOT/scripts/install/install_python_requirements.sh
bash $PROJECT_ROOT/scripts/install/install_network_utilities.sh
bash $PROJECT_ROOT/scripts/database/create_postgres_user.sh
bash $PROJECT_ROOT/scripts/database/create_database.sh
bash $PROJECT_ROOT/scripts/database/migrate_database.sh
bash $PROJECT_ROOT/scripts/database/create_project_users.sh
