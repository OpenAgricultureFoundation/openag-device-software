#! /bin/bash

# curl -X POST --header "Content-Type:application/json" --data '{"appId": '"$BALENA_APP_ID"'}' "$BALENA_SUPERVISOR_ADDRESS/v1/restart?apikey=$BALENA_SUPERVISOR_API_KEY"
# rm /data/network.configured
curl -X POST --header "Content-Type:application/json" "$BALENA_SUPERVISOR_ADDRESS/v1/reboot?apikey=$BALENA_SUPERVISOR_API_KEY"