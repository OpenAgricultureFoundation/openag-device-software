# Installation on a Beaglebone Black Wireless from Source
1. Download [Debian Stretch IoT Image](https://beagleboard.org/latest-images)
2. Flash image to [micro sd card](https://goo.gl/GHaCMB) with [Balena Etcher](https://www.balena.io/etcher/) and insert into beaglebone
3. Connect to beaglebone wifi access point (SSID: BeagleBone-XXXX, PWD: BeagleBone)
4. Login to beaglebone
```
ssh debian@192.168.8.1  # password: temppwd
```
5. Expand the file system
```
df -h /  # view current partition size
sudo /opt/scripts/tools/grow_partition.sh
sudo reboot
df -h /  # View updated partition size
```
6. Copy & paste [get_wifi_ssids_beaglebone.sh](../../scripts/network/get_wifi_ssids_beaglebone.sh) and [join_wifi_beaglebone.sh](../../scripts/network/join_wifi_beaglebone.sh) scripts onto device
```
cd ~
nano get_wifi_ssids_beaglebone.sh  # Paste in code from script (see link)
nano join_wifi_beaglebone.sh  # Paste in code from script (see link)
chmod +x get_wifi_ssids_beaglebone.sh join_wifi_beaglebone.sh
```
7. Connect beaglebone to wifi network
```
./get_wifi_ssids_beaglebone.sh
sudo ./join_wifi_beaglebone.sh <wifi-ssid> <wifi-password>
ping google.com  # verify network is connected
```
8. Update & Upgrade Software
```
sudo apt-get update -y && sudo apt-get upgrade -y
# When prompted, choose to not use the robotics cape and select none for the initial boot program
```
9. Clone project repository
```
cd ~
git clone https://github.com/OpenAgInitiative/openag-device-software.git
```
10. Install the software in preferred runtime mode
```
cd ~/openag-device-software
sudo ./install.sh --<runtime-mode>  # either --development or --production
```
11. Verify the install
```
ps aux | grep autossh  # for both production and development
ps aux | grep python  # for production only
./run.sh  # for development only
```
