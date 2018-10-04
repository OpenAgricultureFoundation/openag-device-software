#!/bin/bash

# Get the full path to this script, the top dir is one up.
TOPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOPDIR+=/..
cd $TOPDIR

# Cache all downloaded pip packages, so we can put in our deb. pkg.
source venv/bin/activate
pip3 download -d venv/pip_download -r requirements.txt

# Also install any new packages we have downloaded (used by the next step)
pip3 install -f venv/pip_download -r requirements.txt 

# Make sure our default user can access all files when running django
sudo chown -R debian:debian .

# Cache any static resources we use (bootstrap, etc)
python3.6 manage.py collectstatic
