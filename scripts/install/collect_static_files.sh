#!/bin/bash

# Log collection status
echo "Collecting static files"

# Collect static files
sudo python3.6 manage.py collectstatic --clear --link --noinput
