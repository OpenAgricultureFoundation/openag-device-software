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
    wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz -P /usr/local/src
    tar xf /usr/local/src/Python-3.6.5.tar.xz
    bash /usr/local/src/Python-3.6.5/configure
    bash /usr/local/src/Python-3.6.5/make
    sudo bash /usr/local/src/Python-3.6.5/make altinstall
    sudo rm -R /usr/local/src/Python-3.6.5
    rm /usr/local/src/Python-3.6.5.tar.xz

    # Verify install
    INSTALL_PATH=`which python3.6`
    if [[ ! -f "$INSTALL_PATH" ]]; then
      echo "Unable to verify install, unknown error"
      exit 1
    fi

# Install on darwin operating system
elif [[ "$OSTYPE" == "darwin"* ]]; then

    # Check if python3.6 is already installed
    INSTALL_PATH=`which python3.6`
    if [[ -f "$INSTALL_PATH" ]]; then
      echo "Python3.6 is already installed at: $INSTALL_PATH"
      exit 0
    fi

    # Ensure brew is installed
    if [[ ! type brew >/dev/null 2>&1 ]]; then
      echo "Installing brew..."
      /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    fi

    # Install python3.6
    brew install python3  # Does this actually work? How does it know 3.6 vs 3.7?

    # Verify install
    INSTALL_PATH=`which python3.6`
    if [[ ! -f "$INSTALL_PATH" ]]; then
      echo "Unable to verify install, unknown error"
      exit 1
    fi

# Invalid operating system
else
  echo "Unable to install python3.6, unsupported operating system: $OSTYPE"
  exit 1
fi
