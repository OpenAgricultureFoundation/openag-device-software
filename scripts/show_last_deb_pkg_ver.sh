#!/bin/bash

LASTVER=`dpkg-parsechangelog --show-field Version`
echo "The last version of this debian package is: $LASTVER"
