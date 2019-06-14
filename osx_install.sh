#!/bin/bash

RUNTIME_MODE="DEVELOPMENT"
LOG_LEVEL="DEBUG"
echo RUNTIME_MODE: $RUNTIME_MODE
echo LOG_LEVEL:  $LOG_LEVEL

# Get project root
echo "Getting project root..."
PROJECT_ROOT=`pwd`
echo PROJECT_ROOT: $PROJECT_ROOT

# Install software
echo "Installing software..."
bash $PROJECT_ROOT/scripts/install/initialize_device_config.sh $PROJECT_ROOT 
bash $PROJECT_ROOT/scripts/install/initialize_directory_structure.sh $PROJECT_ROOT
#bash $PROJECT_ROOT/scripts/install/update_operating_system.sh
#bash $PROJECT_ROOT/scripts/install/install_python36.sh
#bash $PROJECT_ROOT/scripts/install/initialize_port80_forwarding.sh
#bash $PROJECT_ROOT/scripts/install/install_misc_dependencies.sh
bash $PROJECT_ROOT/scripts/install/create_virtual_environment.sh $PROJECT_ROOT
bash $PROJECT_ROOT/scripts/install/initialize_virtual_environment_activate.sh $PROJECT_ROOT $LOG_LEVEL $RUNTIME_MODE
source $PROJECT_ROOT/venv/bin/activate
#bash $PROJECT_ROOT/scripts/install/install_pygame.sh
bash $PROJECT_ROOT/scripts/install/osx_install_python_requirements.sh
#bash $PROJECT_ROOT/scripts/install/set_file_ownership.sh
#bash $PROJECT_ROOT/scripts/install/install_network_utilities.sh
bash $PROJECT_ROOT/scripts/database/migrate_database.sh
bash $PROJECT_ROOT/scripts/database/create_project_users.sh
bash $PROJECT_ROOT/scripts/install/collect_static_files.sh
#bash $PROJECT_ROOT/scripts/install/initialize_rc_local.sh $PROJECT_ROOT $RUNTIME_MODE $REMOTE_DEVICE_UI_URL $PLATFORM

