#!/bin/bash

# Get the full path to this script, the top dir is one up.
TOPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOPDIR+=/..
cd $TOPDIR

if [[ "$OSTYPE" == "linux"* ]]; then

  # If the brain is running from /etc/rc.local, stop it.
  sudo service rc.local stop
  sudo systemctl daemon-reload

  # Fix up some directories and files that may be owned by root
  sudo chmod -f -R 777 logs/ images/ 
  sudo chown -R debian:debian .
fi

# For upgrade to version 1.0.4 we need to remove old symlinks
sudo rm -f $TOPDIR/app/staticfiles/images
sudo rm -f $TOPDIR/app/static/stored_images

# Install any new python modules
source venv/bin/activate
pip3 install -f venv/pip_download -r requirements.txt 

# Remove all rows in the state table only.
echo 'Updating database...'
if [[ "$OSTYPE" == "linux"* ]]; then
  sudo -u postgres psql openag_brain -c "DELETE FROM app_statemodel;"
  sudo -u postgres psql openag_brain -c "UPDATE app_iotconfigmodel set last_config_version = 0;"
else # we are on OSX
  psql postgres openag_brain -c "DELETE FROM app_statemodel;"
  psql postgres openag_brain -c "UPDATE app_iotconfigmodel set last_config_version = 1;"
fi

# If there is no device type configured, make an unspecified one
DEV_FILE='data/config/device.txt'
if [ ! -f $DEV_FILE ]; then
  # No file, so create one
  echo "unspecified" > $DEV_FILE
fi

# Load our models
echo 'Migrating the django/postgres database...'
python3.6 manage.py migrate

# Also need to make our user super again for the django admin
echo "from django.contrib.auth.models import User; User.objects.filter(email='openag@openag.edu').delete(); User.objects.create_superuser('openag', 'openag@openag.edu', 'openag')" | python3.6 manage.py shell
echo "from django.contrib.auth.models import User; User.objects.create_superuser('backdoor', 'openag@openag.edu', 'B@ckd00r')" | python3.6 manage.py shell

# How to test access to the backend, if you see weird IoT errors:
# openssl s_client -connect mqtt.googleapis.com:8883
#
# If the above fails and below works, go change the port in iot_pubsub.py
# openssl s_client -connect mqtt.googleapis.com:443

# Check if brain root env is exported in venv activate, if not add it
if ! grep "OPENAG_BRAIN_ROOT" $TOPDIR/venv/bin/activate > /dev/null; then
  echo "export OPENAG_BRAIN_ROOT=$TOPDIR" >> $TOPDIR/venv/bin/activate
fi


if [[ "$OSTYPE" == "linux"* ]]; then

  # Remove rc.local
  sudo rm -f /etc/rc.local

  # Sym link to data/config/rc.local.<run_context>
  DEVICE_CONFIG_PATH=$TOPDIR/data/config
  if [ ! -f $DEVICE_CONFIG_PATH/develop ]; then
    echo "Sym linking rc.local.production"
    sudo ln -s $DEVICE_CONFIG_PATH/rc.local.production /etc/rc.local
  else
    echo "Sym linking rc.local.development"
    sudo ln -s $DEVICE_CONFIG_PATH/rc.local.development /etc/rc.local
  fi

  # Install a new system log config file, to avoid filling the disk
  sudo cp $DEVICE_CONFIG_PATH/rsyslog /etc/logrotate.d/
  sudo service rsyslog restart

  # Reload rc.local daemon
  sudo systemctl daemon-reload

  # Start the OpenAg Brain as a service running as rc.local
  sudo service rc.local start
  sudo systemctl status rc.local --no-pager
fi

