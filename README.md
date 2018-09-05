# OpenAg Device Software
Software for running controlled grow environments on embedded linux devices (e.g. Raspberry Pi, 
Beaglebone, etc.). The two main parts of the code base are the device threads and on-device
app. The device threads coordinate recipes, control loops, and peripheral (sensor/actuator) 
interactions. The on-device django-based app coordinates the interations with the on-device
database and hosts the local device UI (a.k.a. developer UI) + local device API. There is also an MQTT-based iot 
manager for communication with the OpenAg cloud.

## Installation
While this software is designed to be used on any embedded linux microprocessor, the current
harware this codebase is being developed for is the Beagle Bone Black Wireless. If you are 
familiar with a Raspberry Pi, it is effectively the same thing with a few minor differences.

The entire install process includes:
 1. [Purchase a BeagleBone Black](docs/purchase_bbb.md)
 2. [Prepare SD Card Image](docs/prepare_sd.md)
 3. [Flash Image onto BBB](docs/flash_bbb.md)
 4. [Provision BBB](docs/provision_bbb.md)
 5. [User Setup](docs/user_setup.md)

Proceed to [Installation Part 1: Purchase BBB + SD Card](docs/purchase_bbb.md)

## Contributing
This repo is distrubuted on production devices via debian packaging. For local development,
either start with one of the developer images and follow the standard install process. If 
starting fresh:
 1. Clone this repo:
 ```
 cd ~
 git clone https://github.com/OpenAgInitiative/openag-device-software.git
 ```
 2. Enable `developer mode`
 ```
 touch ~/openag-device-software/config/develop
 ```
 3. Run upgrade script
 ```
 cd ~/openag-device-software/
 ./scripts/upgrade.sh
 ```

## Contents
 - [Install Instructions](docs/install.md)
 - [Running Instructions](docs/running.md)
