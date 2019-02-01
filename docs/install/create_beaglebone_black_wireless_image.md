# Create Beaglebone Black Wireless Image
1. Follow the steps to [Install Beaglebone Black Wireless from Source](install_beaglebone_black_wireless_source) with your preferred runtime option
2. Run image prep script
```
bash $PROJECT_ROOT/scripts/install/prepare_image.sh
```
3. Power off the beaglebone then remove the sd card  and insert it into your laptop
4. Copy the contents from the sd card (For Ubuntu 16.04)
```
sudo fdisk -l  # look for /dev/mmcblk0, ignore partitions /dev/mmcblk0p0 or /dev/mmcblk0p1
sudo dd bs=4M if=/dev/mmcblk0 of=openag-device-software-beaglebone-black-<runtime-mode>-<vX.X.X>.img
```
5. Shrink the image to 4GB by following the [Software Bakery Instructions](https://softwarebakery.com//shrinking-images-on-linux)
6. Compress (e.g. zip) and upload the image to the [Google Drive Directory](https://drive.google.com/drive/folders/1D7d_C41UBIzNbxtrBHDVWUtdsq5iDstv?usp=sharing)
