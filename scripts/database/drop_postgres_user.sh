#!/bin/bash

# Log creation status
echo 'Dropping postgres user...'

# Create database on linux operating system
if [[ "$OSTYPE" == "linux"* ]]; then
    sudo -u postgres psql -c "DROP USER openag;"

# Create database on darwin operating system 
elif [[ "$OSTYPE" == "darwin"* ]]; then
    psql postgres -c "DROP USER openag;"

# Unsupported operating system
else
    echo "Unable to create database, unsupported operating system: $OSTYPE"
    exit 1
fi
