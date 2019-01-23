#!/bin/bash

# Log creation status
echo 'Creating postgres user...'

# Create database on linux operating system
if [[ "$OSTYPE" == "linux"* ]]; then
    sudo -u postgres psql -c "CREATE USER openag WITH PASSWORD 'openag';"
    sudo -u postgres psql -c "ALTER USER openag SUPERUSER;"

# Create database on darwin operating system 
elif [[ "$OSTYPE" == "darwin"* ]]; then
    psql postgres -c "CREATE USER openag WITH PASSWORD 'openag';"
    psql postgres -c "ALTER USER openag SUPERUSER;"

# Unsupported operating system
else
    echo "Unable to create database, unsupported operating system: $OSTYPE"
    exit 1
fi
