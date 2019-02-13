#!/bin/bash

# Log setting status
echo "Setting file ownership"

# Do nothing on OSX operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    exit 0    
fi

# Set file ownership
sudo chown -R $USER:$USER $PROJECT_ROOT
