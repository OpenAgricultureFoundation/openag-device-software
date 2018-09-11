#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Error: missing mandatory command line arg."
    echo "Usage: <full path to .deb file>"
    exit 1
fi

cp $1 ~/package_archive/

reprepro -Vb . includedeb stretch $1
