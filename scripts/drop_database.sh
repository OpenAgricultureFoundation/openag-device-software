#!/bin/bash

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

