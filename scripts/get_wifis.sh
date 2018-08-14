#!/bin/sh
connmanctl tether wifi off > /dev/null 2>&1
connmanctl enable wifi > /dev/null 2>&1
connmanctl scan wifi > /dev/null 2>&1
sleep 2
connmanctl services
