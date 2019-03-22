#!/bin/bash

# Log drop status
echo 'Dropping state table...'

# Drop state table on linux operating system
if [[ "$OSTYPE" == "linux"* ]]; then
  sudo -u postgres psql openag_brain -c "DELETE FROM app_statemodel;"

# Drop state table on darwin operating system
elif [[ "$OSTYPE" == "darwin"* ]]; then
  psql --dbname=postgres --username=openag openag_brain -c "DELETE FROM app_statemodel;"

# Invalid operating system
else
	echo "Unable to drop state table, unsupported operating system: $OSTYPE"
    exit 1
fi
