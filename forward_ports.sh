#!/bin/bash
function jsonval {
    temp=`echo $json | sed 's/\\\\\//\//g' | sed 's/[{}]//g' | awk -v k="text" '{n=split($0,a,","); for (i=1; i<=n; i++) print a[i]}' | sed 's/\"\:\"/\|/g' | sed 's/[\,]/ /g' | sed 's/\"//g' | grep -w $prop | cut -d":" -f2 | sed -e 's/^ *//g' -e 's/ *$//g' `
    echo ${temp##*|}
}

json=`cat about.json`
prop='serial_number'
serial_number=`jsonval`

if [[ "$serial_number" = "" ]] || [[ "$serial_number" = "<DEVICE>-<VERSION>-<ID>" ]]; then
	echo Device serial number not set, please edit about.json
else
	subdomain=`echo "$serial_number" | sed -r 's/[-]+/./g'`
	echo Forwarding ports with subdomain: $subdomain
	autossh -M 0 -R $subdomain.serveo.net:80:localhost:80 serveo.net -R $subdomain:22:localhost:22 serveo.net -oServerAliveInterval=30 -oStrictHostKeyChecking=no -f
fi
