#!/bin/bash

# Set platform variables
source $PROJECT_ROOT/scripts/platform/get_platform_info.sh

# Set network variables
source $PROJECT_ROOT/scripts/network/get_network_settings.sh

# Set google iot variables
source $PROJECT_ROOT/scripts/iot/get_iot_settings.sh $PROJECT_ROOT
