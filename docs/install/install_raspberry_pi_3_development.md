# Installation on a Raspberry Pi 3 for Development from Image
1. Download [Latest Raspberry Pi 3 Development Image (WIP)](https://media0.giphy.com/media/gcZxPiUFzoHgA/giphy.gif?cid=3640f6095c41864c2f56454c6fd3dcea)
2. Flash image to [micro sd card](https://goo.gl/GHaCMB) with [Balena Etcher](https://www.balena.io/etcher/) and insert into raspberry pi
3. Connect raspberry pi to monitor, keyboard, and ethernet cable then power on
4. Make a note of the IP address from the console output. Look for the line "My IP address is <ip-address>"
5. Login to raspberry pi via ssh from your laptop
```
ssh pi@<ip-address>  # password: openag12 (if that doesn't work try raspberry)
```
6. Run the software
```
cd ~/openag-device-software
./run.sh
``
