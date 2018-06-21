#!/bin/bash
cd ~/openag-device-software
source venv/bin/activate
cd device/peripherals/modules/led_dac5578
python scripts/run_panel.py --device edu002 --off
