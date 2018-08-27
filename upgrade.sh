#!/bin/bash

if [[ "$OSTYPE" == "linux"* ]]; then

  # If the brain is running from /etc/rc.local, stop it.
  sudo service rc.local stop

  # Fix up some directories and files that may be owned by root
  sudo chmod -f -R 777 logs/ images/ 
  #sudo chown -f -R debian:debian logs images
fi

# Install any new python modules
source venv/bin/activate
pip install -r requirements.txt

# Recreate a fresh (empty) database
echo 'Recreating database...'
if [[ "$OSTYPE" == "linux"* ]]; then
  sudo -u postgres psql -c "DROP DATABASE openag_brain;"
  sudo -u postgres psql -c "CREATE DATABASE openag_brain OWNER openag;"
  sudo -u postgres psql -c "ALTER USER openag SUPERUSER;"
else # we are on OSX
  psql postgres -c "DROP DATABASE openag_brain;"
  psql postgres -c "CREATE DATABASE openag_brain OWNER openag;"
  psql postgres -c "ALTER USER openag SUPERUSER;"
fi

# Load our models
echo 'Creating the django/postgres database...'
python manage.py migrate

# Also need to make our user super again for the django admin
echo "from django.contrib.auth.models import User; User.objects.filter(email='openag@openag.edu').delete(); User.objects.create_superuser('openag', 'openag@openag.edu', 'openag')" | python manage.py shell

# How to test access to the backend, if you see weird IoT errors:
# openssl s_client -connect mqtt.googleapis.com:8883

# Check if brain root env is exported in venv activate, if not add it
cwd=`pwd`
if ! grep "OPENAG_BRAIN_ROOT" $cwd/venv/bin/activate > /dev/null; then
   echo "export OPENAG_BRAIN_ROOT=$cwd" >> $cwd/venv/bin/activate
fi

# Remove rc.local and sym link to openag-device-software/config/rc.local
sudo rm -f /etc/rc.local
sudo ln -s $cwd/config/rc.local /etc/rc.local
