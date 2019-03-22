#!/bin/bash

# Get the full path to this script, the top dir is one up.
TOPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOPDIR+=/..
cd $TOPDIR

mkdir -p logs/peripherals/
touch app.log connect.log device.log iot.log resource.log upgrade.log

rm -fr venv
python3.6 -m venv venv
source venv/bin/activate

./scripts/download_pip_packages.sh
pip3 install -f venv/pip_download -r requirements.txt 


#debugrob, drop DB first!   it is probably set for master branch.
psql --dbname=postgres --username=openag -c "DROP DATABASE openag_brain;"
psql --dbname=postgres --username=openag -c "CREATE DATABASE openag_brain OWNER openag;"

psql --dbname=postgres --username=openag -c "CREATE USER openag WITH PASSWORD 'openag';"
psql --dbname=postgres --username=openag -c "ALTER USER openag SUPERUSER;"
psql --dbname=postgres --username=openag -c "CREATE DATABASE openag_brain OWNER openag;"

echo 'Creating the django/postgres database...'
python3.6 manage.py migrate

psql --dbname=openag_brain --username=openag -c "UPDATE app_iotconfigmodel set last_config_version = 0;"

echo 'Creating the django/postgres admin account...'
echo "from django.contrib.auth.models import User; User.objects.filter(email='openag@openag.edu').delete(); User.objects.create_superuser('openag', 'openag@openag.edu', 'openag')" | python3.6 manage.py shell
echo "from django.contrib.auth.models import User; User.objects.create_superuser('backdoor', 'openag@openag.edu', 'B@ckd00r')" | python3.6 manage.py shell


