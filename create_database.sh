#!/bin/bash

if [[ "$OSTYPE" == "linux"* ]]; then
  sudo -u postgres psql -c "CREATE USER openag WITH PASSWORD 'openag';"
  sudo -u postgres psql -c "CREATE DATABASE openag_brain OWNER openag;"
else
  psql postgres -c "CREATE USER openag WITH PASSWORD 'openag';"
  psql postgres -c "CREATE DATABASE openag_brain OWNER openag;"
fi

# How to list the databases:
# psql --username=openag openag_brain -c '\d'

# How to log into postgres interactively:
# psql --username=openag openag_brain 

