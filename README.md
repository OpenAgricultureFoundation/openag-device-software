# OpenAg Device Software
Software for running controlled grow environments on embedded linux devices such Raspberry Pi and Beaglebone. 

## Overview
This software is designed to be used on any embedded linux devices. 
It currently supports the Beaglebone, Raspberry Pi, and Standalone Linux-machines with a usb-to-i2c dongle.
It can easily be adaped to a new platform such as a Dragonboard 410C or an Orange Pi.
The two main parts of the code base are the device threads and on-device app. 
The device threads coordinate recipes, control loops, and peripheral (sensor/actuator) interactions. 
The on-device django-based app coordinates the interactions with the on-device database and hosts a local device UI and API. 
There is also an MQTT-based iot manager for communication with the OpenAg cloud.

## Introductory Videos
1. [Getting Started](https://youtu.be/M3rPBoFnRuo)
2. [Architecture Overview](https://youtu.be/tYYAANnXESI) 
3. [Device Overview](https://youtu.be/lotOETQ6RsQ)
4. [App Overview](https://youtu.be/2YWZdtC_ApQ)
5. [Data Overview](https://youtu.be/DeByYZ-9yeI)
6. [Scripts Overview](https://youtu.be/glc1fmoQOr4)
7. [Tests, Type Checks, Coding Conventions](https://youtu.be/USms_7X83aE)

## Installation Instructions
 - [Raspberry Pi 3 Production](docs/install/install_raspberry_pi_3_production.md)
 - [Raspberry Pi 3 Development (From Image)](docs/install/install_raspberry_pi_3_development_image.md)
 - [Raspberry Pi 3 Development (From Source)](docs/install/install_raspberry_pi_3_development_source.md)
 - [Beaglebone Black Wireless Production](docs/install/install_beaglebone_black_wireless_production.md)
 - [Beaglebone Black Wireless Development (From Image)](docs/install/install_beaglebone_black_wireless_development_image.md)
 - [Beaglebone Black Wireless Development (From Source)](docs/install/install_beaglebone_black_wireless_development_source.md)
 - [Linux Machine (e.g. Laptop or Fanless PC)](docs/install/install_linux_machine.md)

## Contributing Instructions
See [Contributing](docs/contributing.md) for links to our forum and wiki.

## Design Documents
 - [Light Control](docs/light/overview.md).
