#!/bin/bash

rm -fr venv
virtualenv -p python3.6 venv
source venv/bin/activate
pip install -r requirements.txt

echo 'Creating the django/postgres database...'
python manage.py migrate

echo 'Creating the django/postgres admin account:'
python manage.py createsuperuser

echo 'Creating our internal postgres application account...'
if [[ "$OSTYPE" == "linux"* ]]; then
  sudo -u postgres psql -c "CREATE USER openag WITH PASSWORD 'openag';"
  sudo -u postgres psql -c "CREATE DATABASE openag_brain OWNER openag;"
else # we are on OSX
  psql postgres -c "CREATE USER openag WITH PASSWORD 'openag';"
  psql postgres -c "CREATE DATABASE openag_brain OWNER openag;"
fi

# How to list the tables in our database:
# psql --username=openag openag_brain -c '\dt'

# How to log into postgres interactively:
# psql --username=openag openag_brain 

