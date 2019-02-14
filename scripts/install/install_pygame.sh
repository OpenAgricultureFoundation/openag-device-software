#!/bin/bash

# Log installation status
echo "Installing pygame..."

# Ensure virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]] ; then
    echo "Please activate your virtual environment then re-run script"
    exit 0
fi

# Install on linux
if [[ ("$PLATFORM" == "raspberry-pi"*) || ("$PLATFORM" == "beaglebone"*) ]]; then
    sudo apt-get install python3-dev python3-numpy libsdl-dev \
        libsdl-image1.2-dev \
        libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libportmidi-dev \
        libavformat-dev libswscale-dev libjpeg-dev libfreetype6-dev -y

    sudo apt install libsdl1.2-dev

    sudo apt-get install mercurial -y
    hg clone https://bitbucket.org/pygame/pygame /tmp/pygame
    cd /tmp/pygame
    python3.6 setup.py build
    sudo python3.6 setup.py install
    cd $PROJECT_ROOT
    sudo rm -r /tmp/pygame
fi
