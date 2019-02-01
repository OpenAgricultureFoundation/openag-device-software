# Create Raspberry Pi 3 Image
1. Follow the steps to [Install Raspberry Pi 3 from Source](install_raspberry_pi_3_source) with your preferred runtime option
2. Make sure you can see the raspberry pi wifi access point from your laptop `RaspberryPi-XXXX`
3. Run image prep script
```
bash $PROJECT_ROOT/scripts/install/prepare_image.sh &  # need to run in background b/c will lose network connectivity if sshing over wifi
```
4. Power off the raspberry pi then remove the sd card  and insert it into your laptop
5. Copy the contents from the sd card (For Ubuntu 16.04)
```
sudo fdisk -l  # look for /dev/mmcblk0, ignore partitions /dev/mmcblk0p0 or /dev/mmcblk0p1
sudo dd bs=4M if=/dev/mmcblk0 of=openag-device-software-raspberry-pi-3-<runtime-mode>-<vX.X.X>.img
```
6. Shrink the image by following the [PiShrink Instructions](https://github.com/Drewsif/PiShrink)
7. Compress (e.g. zip) and upload the image to the [Google Drive Directory](https://drive.google.com/drive/folders/1D7d_C41UBIzNbxtrBHDVWUtdsq5iDstv?usp=sharing)
