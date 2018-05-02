#!/bin/bash

sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install postgresql -y
sudo apt-get install postgresql-contrib -y
sudo apt-get install python-psycopg2 -y
sudo apt-get install libpq-dev -y
sudo apt-get install python3-pip -y