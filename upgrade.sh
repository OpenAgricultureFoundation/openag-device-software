#!/bin/bash

# Get the latest code
git pull

# Install any new python modules
source venv/bin/activate
pip install -r requirements.txt

# Recreate a fresh (empty) database
echo 'Recreating database...'
if [[ "$OSTYPE" == "linux"* ]]; then
  sudo -u postgres psql -c "DROP DATABASE openag_brain;"
  sudo -u postgres psql -c "CREATE DATABASE openag_brain OWNER openag;"
else # we are on OSX
  psql postgres -c "DROP DATABASE openag_brain;"
  psql postgres -c "CREATE DATABASE openag_brain OWNER openag;"
fi

# Load our models
echo 'Creating the django/postgres database...'
python manage.py migrate

# Clean up any files we don't need
rm logs/*.log logs/peripherals/*.log images/*.png


