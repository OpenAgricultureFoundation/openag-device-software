#!/bin/sh
connmanctl tether wifi off > /dev/null 2>&1
connmanctl enable wifi > /dev/null 2>&1
connmanctl scan wifi
sleep 2
connmanctl services
