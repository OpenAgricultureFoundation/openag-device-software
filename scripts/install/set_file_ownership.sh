#!/bin/bash

# Log setting status
echo "Setting file ownership"

# Set file ownership
sudo chown -R $USER:$USER $PROJECT_ROOT
