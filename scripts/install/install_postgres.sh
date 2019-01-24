#!/bin/bash

# Log install status
echo "Installing postgres..."

# Install on linux operating system
if [[ "$OSTYPE" == "linux"* ]]; then

    # Check if postgres is already installed
    INSTALL_PATH=`which psql`
    if [[ -f "$INSTALL_PATH" ]]; then
      echo "Postgres is already installed at: $INSTALL_PATH"
      exit 0
    fi

    # Install postgres
    sudo apt-get install postgresql -y
    sudo apt-get install postgresql-contrib -y
    sudo apt-get install python-psycopg2 -y
    sudo apt-get install libpq-dev -y

    # Verify install
    INSTALL_PATH=`which psql`
    if [[ ! -f "$INSTALL_PATH" ]]; then
      echo "Unable to verify install, unknown error"
      exit 1
    else
      echo "Successfully installed postgres"
    fi

# Install on darwin operating system
elif [[ "$OSTYPE" == "darwin"* ]]; then

    # Check if postgres is already installed
    INSTALL_PATH=`which psql`
    if [[ -f "$INSTALL_PATH" ]]; then
      echo "Postgres is already installed at: $INSTALL_PATH"
      exit 0
    fi

    # Install postgres
    brew install postgresql
    brew services start postgresql

    # Verify install
    INSTALL_PATH=`which psql`
    if [[ ! -f "$INSTALL_PATH" ]]; then
      echo "Unable to verify install, unknown error"
      exit 1
    else
      echo "Successfully installed postgres"
    fi

# Invalid operating system
else
  echo "Unable to install postgres, unsupported operating system: $OSTYPE"
  exit 1
fi
