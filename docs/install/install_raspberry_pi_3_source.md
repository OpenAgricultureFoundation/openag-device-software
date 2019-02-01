# Installation on a Raspberry Pi 3 from Source
1. Download [Raspbian Stretch Lite Image](https://www.raspberrypi.org/downloads/raspbian/)
2. Flash image to [micro sd card](https://goo.gl/GHaCMB) with [Balena Etcher](https://www.balena.io/etcher/) and insert into raspberry pi
3. Connect raspberry pi to monitor and keyboard then power on
5. Login to the raspberry pi with `username: pi` and `password: raspberry`
6. Enable the ssh and i2c interface then set keyboard layout
```
sudo raspi-config
# To enable SSH:
#     Select Option 5: Interfacing Options --> P2: SSH --> Enabled? Yes --> OK
#
# To enable I2C
#     Select Option 5: Interfacing Options --> P5: I2C --> Enabled? Yes --> OK
#
# To set keyboard layout
#    Select Option 4: Localisation Options --> I3: Change Keyboard Layout --> OK --> Other (If not in UK) --> English (US) --> OK
```
7. Set wifi network credentials
```
nano /etc/wpa_supplicant/wpa_supplicant.conf
# Add to the bottom of the file:
network={
    ssid="<wifi-ssid>"
    psk="<wifi-password>"
}
```
Example:
```
<wifi-ssid> = HomeNetwork1
<wifi-ssid> = password1
```
8. Reboot the system
```
sudo reboot
```
9. Take note of your raspberry pi ip address from line that says `My IP address is <ip-address>`
10. Login to raspberry pi via ssh from your laptop
```
# Make sure your laptop is on the same network as your raspberry pi
ssh pi@<ip-address>  # password: raspberry

# If you didn't make a note of your ip address you can get it by runnning: ifconfig
```
11. Install git
```
sudo apt-get install git -y
```
12. Install remote sublime for easy remote text editing 
```
sudo wget -O /usr/local/bin/subl https://raw.github.com/aurora/rmate/master/rmate && sudo chmod +x /usr/local/bin/subl
```
13. Clone project repository
```
cd ~
git clone https://github.com/OpenAgInitiative/openag-device-software.git
```
14. Install the software in preferred runtime mode
```
cd ~/openag-device-software
sudo ./install.sh --<runtime-mode>  # either --development or --production
```
15.  Verify the install
```
ps aux | grep autossh  # for both production and development
ps aux | grep python  # for production only
./run.sh  # for development only
```
