## Create Beaglebone Black Wireless Production Image
1. Follow the steps to [Install Beaglebone Black Wireless for Development from Source](../docs/install/install_beaglebone_black_wireless_development_source) but install with the `--production` option instead
2. Change the password to something more secure
```
passwd  # default password is temppwd
```
3. Power off the beaglebone then remove the sd card  and insert it into your laptop
4. Copy the contents from the sd card (For Ubuntu 16.04)
```
sudo fdisk -l  # list connected disks
# Look for /dev/sdb or /dev/sdc, ignore partitions /sdb/sdb1, /sdb/bd2, /sdb/sdb3, etc.


```
