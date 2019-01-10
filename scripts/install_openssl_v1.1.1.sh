#! /bin/bash

echo "Downloading openssl v1.1.1"
cd ~/Downloads
wget https://www.openssl.org/source/openssl-1.1.1a.tar.gz
tar -zxf openssl-1.1.1a.tar.gz
cd openssl-1.1.1a

echo "Configuring openssl"
sudo ./config

echo "Making openssl"
sudo make

echo "Installing openssl"
sudo make install
sudo mv /usr/bin/openssl ~/tmp
sudo ln -s /usr/local/bin/openssl /usr/bin/openssl
sudo ldconfig
