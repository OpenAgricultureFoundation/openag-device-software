# Installation on a Beaglebone Black Wireless for Development from Image
1. Download [Latest Wireless Beaglebone Black Wireless Development Image (WIP)](https://media0.giphy.com/media/gcZxPiUFzoHgA/giphy.gif?cid=3640f6095c41864c2f56454c6fd3dcea)
2. Flash image to [micro sd card](https://goo.gl/GHaCMB) with [Balena Etcher](https://www.balena.io/etcher/) and insert into beaglebone
3. Connect to beaglebone wifi access point (SSID: BeagleBone-XXXX, PWD: BeagleBone)
4. Login to beaglebone
```
ssh debian@192.168.8.1  # password: openag12 (if that doesn't work try temppwd)
```
5. Run the software
```
cd ~/openag-device-software
./run.sh
```
