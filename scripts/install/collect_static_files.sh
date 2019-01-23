#!/bin/bash

# Save the path to THIS script (before we go changing dirs)
TOPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# The top of our source tree is the parent of this scripts dir
TOPDIR+=/..
cd $TOPDIR

# If there is a current python virtual environment, deactivate it.
if ! [ -z "${VIRTUAL_ENV}" ] ; then
    deactivate
fi

# Activate the python env for this bash process
source $TOPDIR/venv/bin/activate

# Collect static files
sudo venv/bin/python3.6 manage.py collectstatic --clear --link --noinput
