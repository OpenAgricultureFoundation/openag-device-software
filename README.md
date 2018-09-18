# OpenAg Device Software
Software for running controlled grow environments on embedded linux devices (e.g. Raspberry Pi, Beaglebone, etc.). The two main parts of the code base are the device threads and on-device app. The device threads coordinate recipes, control loops, and peripheral (sensor/actuator) interactions. The on-device django-based app coordinates the interations with the on-device database and hosts the local device UI (a.k.a. developer UI) + local device API. There is also an MQTT-based iot manager for communication with the OpenAg cloud.

## Installation
While this software is designed to be used on any embedded linux microprocessor, the current harware this codebase is being developed for is the Beagle Bone Black Wireless. If you are familiar with a Raspberry Pi, it is effectively the same thing with a few minor differences.

The entire install process includes:
 1. [Purchase a BeagleBone Black](docs/purchase_bbb.md).
 2. [Prepare SD Card Image](docs/prepare_sd.md).
 3. [Flash Image onto BBB](docs/flash_bbb.md).
 4. [Provision BBB](docs/provision_bbb.md).
 5. [User Setup](docs/user_setup.md).

Proceed to [Installation Part 1: Purchase BBB + SD Card](docs/purchase_bbb.md)

## Contributing to the software projects
See [Contributing](docs/contributing.md) for links to our forum and wiki.

This repo is distrubuted on production devices via debian packaging. For local development you have 3 choices:
 1. Start with one of the developer BBB images.  Follow step 3: [Flash Image onto BBB](docs/flash_bbb.md).
 2. Start with a brand new BBB.  Follow step 2: [Prepare SD Card Image](docs/prepare_sd.md).
 3. Use your OSX or Linux machine and use the **Getting the code** steps below.


### Getting the code
 - [Install Instructions](docs/install.md)
