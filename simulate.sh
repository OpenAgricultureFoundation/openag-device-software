#!/bin/bash

# If you get errors from http://127.0.0.1
# Use --no-device on the command line to clean up state DB.
# Then nav to http://127.0.0.1/admin
# Go to state model and delete object.

# Run the Jbrain in simulation mode (for development on OSX, Ubuntu, etc. when 
# you don't have an I2C bus).
./run.sh --simulate $@

