# Installation on a Beaglebone Black Wireless for Development from Source
1. Download [Debian Stretch IoT Image](https://beagleboard.org/latest-images)
2. Flash image to [micro sd card](https://goo.gl/GHaCMB) with [Balena Etcher](https://www.balena.io/etcher/) and insert into beaglebone
3. Connect to beaglebone wifi access point (SSID: BeagleBone-XXXX, PWD: BeagleBone)
4. Login to beaglebone
```
ssh debian@192.168.8.1  # password: temppwd
```
5. Copy & paste [get_wifi_ssids_beaglebone.sh](../scripts/network/get_wifi_ssids_beaglebone.sh) and [join_wifi_beaglebone.sh](../scripts/network/join_wifi_beaglebone.sh) scripts onto device
```
cd ~
nano get_wifi_ssids_beaglebone.sh  # Paste in code from script (see link)
nano join_wifi_beaglebone.sh  # Paste in code from script (see link)
chmod +x get_wifi_ssids_beaglebone.sh join_wifi_beaglebone.sh
```
6. Connect beaglebone to wifi network
```
./get_wifi_ssids_beaglebone.sh
sudo ./join_wifi_beaglebone.sh <wifi-ssid> <wifi-password>
ping google.com  # To verify network is connected
```
7. Update & Upgrade Software
```
sudo apt-get update -y
 sudo apt-get upgrade -y
# When prompted, choose to not use the robotics cape and select none for the initial boot program
```
7. Clone project repository
```
cd ~
git clone https://github.com/OpenAgInitiative/openag-device-software.git
```
8. Install the software in development mode
```
cd ~/openag-device-software
./install.sh --development
```
9. Run the software
```
cd ~/openag-device-software
./run.sh
```
