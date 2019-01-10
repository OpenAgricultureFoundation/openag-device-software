#!/bin/bash

if [[ "$OSTYPE" == "linux"* ]]; then
  # Our production install for Debian 9.3 on the BBB. (also Ubuntu for dev)
  sudo apt-get update -y
  sudo apt-get upgrade -y
  sudo apt-get install postgresql -y
  sudo apt-get install postgresql-contrib -y
  sudo apt-get install python-psycopg2 -y
  sudo apt-get install libpq-dev -y
  sudo apt-get install python3-pip -y

elif [[ "$OSTYPE" == "darwin"* ]]; then
  # Development install on OSX
  # Please run "brew upgrade" if it is recommended (it will fix python3 issues)
  if ! type brew >/dev/null 2>&1; then
    echo 'Installing brew:'
    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
  fi

  if ! type python3 >/dev/null 2>&1; then
    echo 'Installing python3:'
    brew install python3
  fi

  if ! type pip3 >/dev/null 2>&1; then
    echo 'Installing pip3 (should have been installed with py3):'
    brew install python3
  fi

  # Always need to install/reinstall venv
  echo 'Installing virtualenv:'
  pip3 install virtualenv

  if ! type postgres >/dev/null 2>&1; then
    echo 'Installing postgresql:'
    brew install postgresql
    # Start postgres now, and upon every reboot
    brew services start postgresql
  fi

else
  echo "Unsupported OS: $OSTYPE, please manually install postgres and python3"
fi

# Install the python static type checker - used when testing.
python3 -m pip install -U mypy

# if you are a VIM geek:  https://github.com/Integralist/vim-mypy

# Install autossh for persistent ssh forwarding
sudo apt-get install autossh

# Install busybox for hosting images
sudo apt-get install busybox
