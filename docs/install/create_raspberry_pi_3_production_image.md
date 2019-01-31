## Create Raspberry Pi 3 Production Image
1. Follow the steps to [Install Raspberry Pi 3 for Development from Source](../docs/install/install_raspberry_pi_3_development_source) but install with the `--production` option instead
2. Make sure the software is running
```
ps aux | grep python
ps aux | grep autossh
```
3. Change the password to something more secure
```
passwd  # default password is raspberry
```
4. Disconnect the raspberry pi from any network connection and reconnect to it with a display and keyboard
5. Delete the iot registration data directory
```
sudo rm -rf ~/openag-device-software/data/registration
```
6. Make sure you can see the raspberry pi wifi access point from your laptop `RaspberryPi-XXXX`
7. Power off the raspberry pi then remove the sd card  and insert it into your laptop
8. Copy the contents from the sd card (For Ubuntu 16.04)
```
sudo fdisk -l  # list connected disks
# Look for /dev/sdb or /dev/sdc, ignore partitions /sdb/sdb1, /sdb/bd2, /sdb/sdb3, etc.
# Alternatively look for /dev/mmcblk0, ignore /dev/mmcblk0p0 and /dev/mmcblk0p1
sudo dd bs=4M if=/dev/sdb of=<image-name>.img  # copy contents of sd card

```
9. Install [PiShrink](https://github.com/Drewsif/PiShrink)
10. Shrink the image size
```
sudo pishrink.sh <image-name>.img
```
