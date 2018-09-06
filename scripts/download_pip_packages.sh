#!/bin/bash

# Get the full path to this script, the top dir is one up.
TOPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOPDIR+=/..
cd $TOPDIR

# Cache all downloaded pip packages, so we can put in our deb. pkg.
source venv/bin/activate
pip3 download -d venv/pip_download -r requirements.txt
