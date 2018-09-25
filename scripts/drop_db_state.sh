#!/bin/bash

# Remove all rows in the state table only.
echo 'Dropping state database...'
if [[ "$OSTYPE" == "linux"* ]]; then
  sudo -u postgres psql openag_brain -c "DELETE FROM app_statemodel;"
else # we are on OSX
  psql postgres openag_brain -c "DELETE FROM app_statemodel;"
fi
