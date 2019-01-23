#!/bin/bash

# Get the full path to this script, the top dir is one up.
TOPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOPDIR+=/..

# Setup log file structure
mkdir -p $TOPDIR/data/logs/peripherals/
cd $TOPDIR/data/logs
touch app.log connect.log device.log iot.log resource.log upgrade.log

# Setup stored image directory
mkdir -p $TOPDIR/data/images/stored
cd $TOPDIR

rm -fr venv
virtualenv -p python3.6 venv
source venv/bin/activate
./scripts/download_pip_packages.sh
pip3 install -f venv/pip_download -r requirements.txt 


echo 'Creating our internal postgres application account...'
if [[ "$OSTYPE" == "linux"* ]]; then
  sudo -u postgres psql -c "CREATE USER openag WITH PASSWORD 'openag';"
  sudo -u postgres psql -c "ALTER USER openag SUPERUSER;"
  sudo -u postgres psql -c "CREATE DATABASE openag_brain OWNER openag;"
else # we are on OSX
  psql postgres -c "CREATE USER openag WITH PASSWORD 'openag';"
  psql postgres -c "ALTER USER openag SUPERUSER;"
  psql postgres -c "CREATE DATABASE openag_brain OWNER openag;"
fi

echo 'Creating the django/postgres database...'
python3.6 manage.py migrate

echo 'Creating the django/postgres admin account...'
echo "from django.contrib.auth.models import User; User.objects.filter(email='openag@openag.edu').delete(); User.objects.create_superuser('openag', 'openag@openag.edu', 'openag')" | python3.6 manage.py shell
echo "from django.contrib.auth.models import User; User.objects.create_superuser('backdoor', 'openag@openag.edu', 'B@ckd00r')" | python3.6 manage.py shell


# How to log into postgres interactively:
# psql --username=openag openag_brain 

