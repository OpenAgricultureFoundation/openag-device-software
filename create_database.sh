#!/bin/bash

sudo -u postgres psql -c "CREATE USER openag WITH PASSWORD 'openag';"
sudo -u postgres psql -c "CREATE DATABASE openag_brain OWNER openag;"

