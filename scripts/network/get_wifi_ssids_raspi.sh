#! /bin/bash

sudo iwlist wlan0 scan | egrep 'ESSID:"[^"]' | cut -d ':' -f 2 | sed -e 's/^"//' -e 's/"$//'
