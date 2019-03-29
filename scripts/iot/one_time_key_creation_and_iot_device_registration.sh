#!/bin/bash

# This script is passed the directory it should change to before creating files.
if [ $# -eq 0 ]; then
    echo "one_time_key_creation_and_iot_device_registration.sh: Error: missing data dir on the command line."
    exit 1
fi
mkdir -p $@
cd $@

# Get the Google root cert
wget -q https://pki.goog/roots.pem

# https://cloud.google.com/iot/docs/how-tos/credentials/keys
# Generate ssh keys for signing
FILE='rsa_cert.pem'
openssl req -x509 -newkey rsa:2048 -days 3650 -keyout rsa_private.pem \
  -nodes -out $FILE -subj "/CN=unused" > /dev/null 2>&1

# Embed escaped newlines in a single string to represent the key file
KEY=`awk 'NF {sub(/\r/, ""); printf "%s\\\n",$0;}' $FILE`

# Python to generate the checksum we show the user as a "validation code"
CKSUM=`python3 -c "import zlib
fn = \"$FILE\"
with open( fn, 'r' ) as f:
  key_file_contents = f.read()
cksum = zlib.crc32( key_file_contents.encode('utf-8') )
print( '{:X}'.format( cksum ))"`

# Python to get this devices MAC address
MAC=`python3 -c "import uuid
mac_addr = hex( uuid.getnode()).replace( '0x', '')
mac = '-'.join( mac_addr[i : i + 2] for i in range( 0, 11, 2))
print( '{}'.format( mac ))"`

# Current UTC timestamp
TIMESTAMP="oops"
if [[ "$OSTYPE" == "linux"* ]]; then
  TIMESTAMP=`date --utc +%FT%TZ`
elif [[ "$OSTYPE" == "darwin"* ]]; then
  TIMESTAMP=`date -u +%FT%TZ`
fi

# Must use " in JSON, hence the funny bash string concatenation for the data
DATA='{"key": "'$KEY'", "cksum": "'$CKSUM'", "MAC": "'$MAC'", "timestamp": "'$TIMESTAMP'"}'

# POST the data to the firebase cloud function
RET=`curl --silent https://us-central1-fb-func-test.cloudfunctions.net/saveKey  -H "Content-Type: application/json" -X POST --data "$DATA"`

if [[ $RET = *"error"* ]]; then
  echo "Error: could not register this device."
  echo $RET
  exit 1
fi

# Must zero out the last IoT message received, so we process messages.
#debugrob TODO do we need to do this for sqlite?
# "UPDATE app_iotconfigmodel set last_config_version = 0;"

# Save this devices ID to a file that the brain startup script will read.
echo "export DEVICE_ID=EDU-$CKSUM-$MAC" > device_id.bash

echo "$CKSUM" > verification_code.txt


