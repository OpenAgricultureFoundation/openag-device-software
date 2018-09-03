#!/bin/bash

if [[ "$OSTYPE" != "linux"* ]]; then
    echo "This script can only be run on a BBB."
    exit 1
fi 

LASTVER=`dpkg-parsechangelog --show-field Version`
echo "The last version of this debian package is: $LASTVER"
