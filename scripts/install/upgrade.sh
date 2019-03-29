#!/bin/bash

# Log upgrade status
echo "Upgrading software..."

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

# Stop currently running software if on linux operating system
if [[ "$OSTYPE" == "linux"* ]]; then
    sudo service rc.local stop
    sudo systemctl daemon-reload
fi

# Install new python requirements
pip3.6 install -f $PROJECT_ROOT/venv/pip_download -r $PROJECT_ROOT/requirements.txt 

# Migrate the database
bash $PROJECT_ROOT/scripts/database/migrate_database.sh

if [[ "$OSTYPE" == "linux"* ]]; then

    # Install a new system log config file, to avoid filling the disk
    sudo cp $DEVICE_CONFIG_PATH/rsyslog /etc/logrotate.d/
    sudo service rsyslog restart

    # Collect static files
    sudo bash $PROJECT_ROOT/scripts/install/collect_static_files.sh

    # Reload rc.local daemon
    sudo systemctl daemon-reload

    # Start the OpenAg Brain as a service running as rc.local
    sudo service rc.local start
    sudo systemctl status rc.local -l --no-pager
fi

