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
  sudo -u postgres psql -c "ALTER USER openag SUPERUSER;"
else # we are on OSX
  psql postgres -c "DROP DATABASE openag_brain;"
  psql postgres -c "CREATE DATABASE openag_brain OWNER openag;"
  psql postgres -c "ALTER USER openag SUPERUSER;"
fi

# Also need to make our user super again for the django admin
echo "from django.contrib.auth.models import User; User.objects.filter(email='openag@openag.edu').delete(); User.objects.create_superuser('openag', 'openag@openag.edu', 'openag')" | python manage.py shell

# Load our models
echo 'Creating the django/postgres database...'
python manage.py migrate


