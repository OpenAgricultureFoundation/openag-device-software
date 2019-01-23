#!/bin/bash

# This script is meant to be run from the top dir like: 
#   ./scripts/publish-to-test-topic.sh

# Publish to this topic instead of the default one.  Assumes you have a local
# MQTT server running, subscribing to the same topic (and subfolder).
#debugrob
#export IOT_TEST_TOPIC=test/test
export IOT_TEST_TOPIC=events/test

./run.sh $@

