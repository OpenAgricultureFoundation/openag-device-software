#!/bin/bash

# This script is meant to be run from the project root

# Publish to this topic instead of the default one.  Assumes you have a local
# MQTT server running, subscribing to the same topic (and subfolder).

# https://cloud.google.com/iot/docs/how-tos/mqtt-bridge#publishing_telemetry_events_to_separate_pubsub_topics

export IOT_TEST_TOPIC="events/test"

#./run.sh $@
./simulate.sh $@
