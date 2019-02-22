# OpenAg Device Software
Software for running controlled grow environments on embedded linux devices such Raspberry Pi and Beaglebone. 

## Overview
This software is designed to be used on any embedded linux devices. 
It currently supports the Beaglebone, Raspberry Pi, and Standalone Linux-machines with a usb-to-i2c dongle.
It can easily be adaped to a new platform such as a Dragonboard 410C or an Orange Pi.
The two main parts of the code base are the device threads and on-device app. 
The device threads coordinate recipes, control loops, and peripheral (sensor/actuator) interactions. 
The on-device django-based app coordinates the interactions with the on-device database and hosts a local device UI and API. 
There is also an MQTT-based IoT manager for communication with the OpenAg cloud service.

## Introductory Videos
1. [Introduction](https://www.youtube.com/watch?v=RByKZJ7bDx8&list=PL7dmhIGxrpXE0EEOFxz7wbVOLJXYAMqE0&index=1)
2. [Getting Started](https://www.youtube.com/watch?v=M3rPBoFnRuo&list=PL7dmhIGxrpXE0EEOFxz7wbVOLJXYAMqE0&index=2)
3. [Architecture Overview](https://www.youtube.com/watch?v=tYYAANnXESI&list=PL7dmhIGxrpXE0EEOFxz7wbVOLJXYAMqE0&index=3) 
4. [Device Overview](https://www.youtube.com/watch?v=lotOETQ6RsQ&list=PL7dmhIGxrpXE0EEOFxz7wbVOLJXYAMqE0&index=4)
5. [App Overview](https://www.youtube.com/watch?v=2YWZdtC_ApQ&list=PL7dmhIGxrpXE0EEOFxz7wbVOLJXYAMqE0&index=5)
6. [Data Overview](https://www.youtube.com/watch?v=DeByYZ-9yeI&list=PL7dmhIGxrpXE0EEOFxz7wbVOLJXYAMqE0&index=6)
7. [Scripts Overview](https://www.youtube.com/watch?v=glc1fmoQOr4&list=PL7dmhIGxrpXE0EEOFxz7wbVOLJXYAMqE0&index=7)
8. [Tests, Type Checks, Coding Conventions](https://www.youtube.com/watch?v=USms_7X83aE&list=PL7dmhIGxrpXE0EEOFxz7wbVOLJXYAMqE0&index=8)

## Installation Instructions
 - [Raspberry Pi 3 Production](docs/install/install_raspberry_pi_3_production.md)
 - [Raspberry Pi 3 Development](docs/install/install_raspberry_pi_3_development.md)
 - [Raspberry Pi 3 Source](docs/install/install_raspberry_pi_3_source.md)
 - [Beaglebone Black Wireless Production](docs/install/install_beaglebone_black_wireless_production.md)
 - [Beaglebone Black Wireless Development](docs/install/install_beaglebone_black_wireless_development.md)
 - [Beaglebone Black Wireless Source](docs/install/install_beaglebone_black_wireless_source.md)
 - [Linux Machine (e.g. Ubuntu Laptop or Fanless PC)](docs/install/install_linux_machine.md)

## Image Creation Instructions
 - [Create Image for Raspberry Pi 3](docs/install/create_raspberry_pi_3_image.md)
 - [Create Image for Beaglebone Black Wireless](docs/install/create_beaglebone_black_wireless_image.md)

## Contributing Instructions
See [Contributing](docs/contributing.md) for links to our forum and wiki.

## Design Documents
 - [Code Structure Diagram](docs/code_structure.png)
 - [System Architecture Diagram](docs/iot_architecture.jpg)
 - [Light Control](docs/light/overview.md)

## Development
See [USB to I2C communication cable](docs/usb_i2c_cable/USB-I2C.md) for I2C development notes.


