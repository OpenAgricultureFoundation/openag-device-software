#!/bin/bash

# Log creation status
echo 'Creating database...'

# Create database on linux operating system
if [[ "$OSTYPE" == "linux"* ]]; then
    sudo -u postgres psql -c "CREATE DATABASE openag_brain OWNER openag;"

# Create database on darwin operating system 
elif [[ "$OSTYPE" == "darwin"* ]]; then
    psql --dbname=postgres --username=openag -c "CREATE DATABASE openag_brain OWNER openag;"

# Unsupported operating system
else
    echo "Unable to create database, unsupported operating system: $OSTYPE"
    exit 1
fi
