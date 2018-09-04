#!/bin/bash

TOPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOPDIR+=/..
cd $TOPDIR

source venv/bin/activate
cd device/peripherals/modules/led_dac5578
python scripts/run_panel.py --device edu-v0.3.0 --fade
