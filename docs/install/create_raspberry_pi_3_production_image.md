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
4. Power off the raspberry pi then remove the sd card  and insert it into your laptop
5. Copy the contents from the sd card (For Ubuntu 16.04)
```
sudo fdisk -l  # list connected disks
# Look for /dev/sdb or /dev/sdc, ignore partitions /sdb/sdb1, /sdb/bd2, /sdb/sdb3, etc.
# Alternatively look for /dev/mmcblk0, ignore /dev/mmcblk0p0 and /dev/mmcblk0p1
sudo dd bs=4M if=/dev/sdb of=<image-name>.img  # copy contents of sd card

```
6. Install [PiShrink](https://github.com/Drewsif/PiShrink)
7. Shrink the image size
```
sudo pishrink.sh <image-name>.img
```
