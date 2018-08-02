# Install Part 2: Prepare SD Card Image

Back to [Part 1: Purchase Beaglebone Black + SD Card](purchase_bbb.md)...or...Forward to [Part 3: Flash Image onto BBB](flash_bbb.md)

**IMPORTANT NOTE:** If you are trying to download the pre-built image do not follow these
steps. Proceed directly to [Part 3: Flash Image onto BBB](flash_bbb.md).

## Install Steps (TODO: pull steps out from wiki)
https://wiki.openag.media.mit.edu/users/rbaynes/notes/bbb/debian

## Started from v0.1.1 image, changelog:
 - Added autossh to install.sh
    ```
    sudo apt-get install autossh
    ```
 - Added remote sublime to image
   ```
   sudo wget -O /usr/local/bin/rsub https://raw.github.com/aurora/rmate/master/rmate
   sudo chmod +x /usr/local/bin/rsub

   # Add to .bashrc
   alias subl='rsub'
   ```
 - Added jake's public SSH keys (fs2 and laptop)
 - Ran upgrade script
   ```
   sudo ./upgrade.sh
   ```
 - Added port forwarding script to to `/etc/rc.local` 
   ```
   #!/bin/sh
   chdir /home/debian/openag-device-software
   /home/debian/openag-device-software/run.sh &
   /home/debian/openag-device-software/forward_ports.sh &
   ```  
 - Uninstalled apache
   ```
   sudo service apache2 stop
   sudo apt-get remove -y apache2

   sudo systemctl stop bonescript.service              
   sudo systemctl stop bonescript.socket
   sudo systemctl stop bonescript-autorun.service

   sudo systemctl disable bonescript.service              
   sudo systemctl disable bonescript.socket
   sudo systemctl disable bonescript-autorun.service

   ps -def | grep node
   sudo kill <node PID>
   ```
 - Changed UI to forward via port 80 (was 8000)


## Before Finalizing Image
 - Stop any python processes from running
   ```
   ps aux | grep python
   sudo kill <pid>
   ```
 - Run `./upgrade.sh` to blow away (and re-initialize) db
 - Blow away registration data
   ```
   sudo rm -r registration/data
   ```

## Copy eMMC to SD Image
 - Boot BBB normally
 - Insert blank SD card
 - SSH into BBB
 - Run flasher script on BBB
   ```
   sudo /opt/scripts/tools/eMMC/beaglebone-black-make-microSD-flasher-from-eMMC.sh
   ```
 - Wait for script to finish and BBB leds to turn off
 - Remove power from BBB
 - Remove SD card from BBB
 - Insert SD card into laptop, copy image as a file, see OS specific instructions

### Copy SD Image to laptop -- Linux (Ubuntu 16.04)
```
fdisk -l /dev/mmcblk0
dd if=/dev/mmcblk0/ | gzip > YYYY-MM-DD_bbb_debX.Y_brain_description.img.gz
```
### Copy SD Image to laptop -- OSX
- Start DiskUtility.
- Select the partition of the SD card.
- Click File > New Image > Image from <your partition name> (usually “Untitled”)
- Provide a file name in the format: YYYY-MM-DD_bbb_debX.Y_brain_description
- Select DVD/CD master from the Format menu on the bottom of the pop-up dialog
- Click Save on the pop-up dialog.
- Rename the .cdr file to .iso

## Test Image is Valid
 - Write image back to a new SD card w/Etcher.io
 - Insert newly flashed SD card into fresh BBB
 - Observe a 'cylon' pattern to verify BBB is being flashed
 - Once all lights shut off power down BBB

## Upload Image to Drive
 - Upload to [FC Operating System Images](https://drive.google.com/drive/folders/1_8qds9_7xkiPrP8CDYuQaFylpPfw_vqI?usp=sharing)
