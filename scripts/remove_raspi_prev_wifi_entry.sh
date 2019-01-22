#! /bin/bash

NUM_LINES=`wc -l < /etc/wpa_supplicant/wpa_supplicant.conf`

if [[ $NUM_LINES -gt 9 ]]; then
	head -n -6 /etc/wpa_supplicant/wpa_supplicant.conf > /etc/wpa_supplicant/tmp
	cp /etc/wpa_supplicant/tmp /etc/wpa_supplicant/wpa_supplicant.conf
fi
