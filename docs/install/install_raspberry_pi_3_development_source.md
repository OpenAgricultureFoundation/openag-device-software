# Installation on a Raspberry Pi 3 for Development from Source
1. Download [Raspbian Stretch Lite Image](https://www.raspberrypi.org/downloads/raspbian/)
2. Flash image to [micro sd card](https://goo.gl/GHaCMB) with [Balena Etcher](https://www.balena.io/etcher/) and insert into raspberry pi
3. Connect raspberry pi to monitor, keyboard, and ethernet cable then power on
4. Make a note of the IP address from the console output. Look for the line "My IP address is <ip-address>"
5. With the keyboard, login to the raspberry pi with `username: pi` and `password: raspberry`
6. Enable the ssh and i2c interface
```
sudo raspi-config
# To enable SSH:
#     Select Option 5: Interfacing Options --> P2: SSH --> Enabled? Yes --> OK
#
# To enable I2C
#     Select Option 5: Interfacing Options --> P5: I2C --> Enabled? Yes --> OK
```
7. Login to raspberry pi via ssh from your laptop
```
# Make sure your laptop is on the same network as your raspberry pi
ssh pi@<ip-address>  # password: raspberry

# If you didn't make a note of your ip address you can get it by runnning: ifconfig
```
8. Install git
```
sudo apt-get install git -y
```
9. Clone project repository
```
cd ~
git clone https://github.com/OpenAgInitiative/openag-device-software.git
```
9. Install the software in development mode
```
cd ~/openag-device-software
./install.sh --development
```
10. Run the software
```
cd ~/openag-device-software
./run.sh
```
