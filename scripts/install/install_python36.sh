#!/bin/bash

# Log install status
echo "Installing python36..."

# Install on linux linux operating system
if [[ "$OSTYPE" == "linux"* ]]; then

        # Check if python3.6 is already installed
        INSTALL_PATH=`which python3.6`
        if [[ -f "$INSTALL_PATH" ]]; then
            echo "Python3.6 is already installed at: $INSTALL_PATH"
            exit 0
        fi
        
        # Install python3.6
        sudo apt-get update
        sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev
        wget https://www.python.org/ftp/python/3.6.8/Python-3.6.8.tar.xz -P /tmp
        sudo tar xf /tmp/Python-3.6.8.tar.xz -C /tmp/
        cd /tmp/Python-3.6.8/
        sudo bash configure
        sudo make -C /tmp/Python-3.6.8/
        sudo make altinstall -C /tmp/Python-3.6.8/
        cd $PROJECT_ROOT
        sudo rm -R /tmp/Python-3.6.8
        rm /tmp/Python-3.6.8.tar.xz

        # Verify install
        INSTALL_PATH=`which python3.6`
        if [[ ! -f "$INSTALL_PATH" ]]; then
            echo "Unable to verify install, unknown error"
            exit 1
        else
          echo "Successfully installed python3.6"
        fi

# Install on OSX operating system
elif [[ "$OSTYPE" == "darwin"* ]]; then

        # Check if python3.6 is already installed
        INSTALL_PATH=`which python3.6`
        if [[ -f "$INSTALL_PATH" ]]; then
            echo "Python3.6 is already installed at: $INSTALL_PATH"
            exit 0
        fi

        # Install python3.6
        echo "Download and install Python3.6 from: https://www.python.org/downloads/mac-osx/"
        exit 0


# Invalid operating system
else
    echo "Unable to install python3.6, unsupported operating system: $OSTYPE"
    exit 1
fi
