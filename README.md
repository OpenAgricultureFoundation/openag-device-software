# OpenAg Device Software
Software for running controlled grow environments on embedded linux devices (e.g. Raspberry Pi, 
Beaglebone, etc.). The two main parts of the code base are the device threads and on-device
app. The device threads coordinate recipes, control loops, and peripheral (sensor/actuator) 
interactions. The on-device django-based app coordinates the interations with the on-device
database and hosts the 'developer' UI + local device API. There is also an MQTT-based iot 
manager for communication with the OpenAg cloud.

## Installation
While this software is designed to be used on any embedded linux microprocessor, the current
harware this codebase is being developed for is the Beagle Bone Black Wireless. If you are 
familiar with a Raspberry Pi, it is effectively the same thing with a few minor differences.

The entire install process includes:
 1. Purchase a [Beagle Bone Black Wireless](https://www.alliedelec.com/beagleboard-beaglebone-black-wireless/71064028/) + [32GB SD Card](https://www.amazon.com/Samsung-Class-Micro-Adapter-MB-MC32DA/dp/B00WR4IJBE/ref=pd_nav_b2b_ab_bia_t_1?_encoding=UTF8&psc=1&refRID=DK0MX84J8CS6QFZ1MTG3)
 2. [Prepare SD Card Image](docs/prepare_sd.md)
 3. [Flash Image onto BBB](docs/flash_bbb.md)
 4. [Provision BBB](docs/provision_bbb.md)
 5. [User Setup](docs/user_setup.md)

Proceed to [Installation Part 1: Purchase BBB + SD Card](docs/purchase_bbb.md)


## Contents
 - [Install Instructions](docs/install.md)
 - [Running Instructions](docs/running.md)
