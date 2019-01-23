#!/bin/bash

# Log recreation status
echo 'Dropping database...'

# Recreate on linux operating system
if [[ "$OSTYPE" == "linux"* ]]; then
  sudo -u postgres psql -c "DROP DATABASE openag_brain;"

# Recreate on darwin operating system
elif [[ "$OSTYPE" == "darwin"* ]]; then
  psql postgres -c "DROP DATABASE openag_brain;"

# Invalid operating system
else
  echo "Unable to drop database, unsupported operating system: $OSTYPE"
  exit 1
fi
