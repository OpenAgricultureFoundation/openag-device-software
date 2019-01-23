#!/bin/bash

# Log creation status
echo "Creating project users..."

# Check virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]] ; then
    echo "Please activate your virtual environment then re-run script"
    exit 1
fi

# Check project root exists
if [[ -z "$PROJECT_ROOT" ]]; then
	echo "Please set your project root in your virtual environment then re-run script"
    exit 1
fi

# Check python3.6 is installed
INSTALL_PATH=`which python3.6`
if [[ ! -f "$INSTALL_PATH" ]]; then
    echo "Please install python3.6 then re-run script"
    exit 1
fi

# Create project users
echo "from django.contrib.auth.models import User; User.objects.filter(email='openag@openag.edu').delete(); User.objects.create_superuser('openag', 'openag@openag.edu', 'openag')" | python3.6 $PROJECT_ROOT/manage.py shell
echo "from django.contrib.auth.models import User; User.objects.create_superuser('backdoor', 'openag@openag.edu', 'B@ckd00r')" | python3.6 $PROJECT_ROOT/manage.py shell
