# Install Part 2: Prepare SD Card Image

Back to [Part 1: Purchase Beaglebone Black + SD Card](purchase_bbb.md)...or...Forward to [Part 3: Flash Image onto BBB](flash_bbb.md)

**IMPORTANT NOTE:** If you are trying to download the pre-built BBB operating system image do not follow these steps. Proceed directly to [Part 3: Flash Image onto BBB](flash_bbb.md).

## Install Steps to apply to a fresh BBB operating system image from http://debian.beagleboard.org

**NOTE:** We are deploying the PFC_EDUs based on this image: http://debian.beagleboard.org/images/bone-debian-9.3-iot-armhf-2018-03-05-4gb.img.xz

## Steps to install the Debian 9.3 image onto a BBB:
1. Use [Etcher](https://etcher.io/) to write a BBB image to an 8G SD card.
2. Connect the USB cable the BBB came with to your machine (it will boot up).
3. Put the 8G SD card in the BBB.
4. `ssh debian@beaglebone.local` with password `temppwd` (or use `ssh debian@192.168.6.2`)
5. Do these steps to prepare the image with the packages and config we need:
```
  sudo apt-get update
  sudo apt-get install -y psmisc   
  sudo apt-get install -y fswebcam
  sudo apt-get install -y autossh
  sudo apt-get install -y postgresql
  sudo apt-get install -y postgresql-contrib
  sudo apt-get install -y python-psycopg2
  sudo apt-get install -y libpq-dev
  sudo apt-get install -y python3-pip

  sudo pip install --upgrade pip
  sudo pip install --upgrade virtualenv
  sudo apt-get install -y openssl libffi-dev libssl-dev

  wget https://packagecloud.io/install/repositories/quan/beaglebone-stretch/script.deb.sh
  sudo bash script.deb.sh
  sudo apt-get install -y python3.6-minimal python3.6-dev

  sudo chmod 777 /var/lib/connman/

  sudo service apache2 stop
  sudo apt-get remove -y apache2

  sudo systemctl stop bonescript.service
  sudo systemctl stop bonescript.socket
  sudo systemctl stop bonescript-autorun.service

  sudo systemctl disable bonescript.service
  sudo systemctl disable bonescript.socket
  sudo systemctl disable bonescript-autorun.service

  sudo bash -c 'wget -O - https://storage.googleapis.com/openag-v1-debian-packages/rbaynes@mit.edu.gpg.key | apt-key add - '
  sudo bash -c 'echo "deb https://storage.googleapis.com/openag-v1-debian-packages/ stretch main" >> /etc/apt/sources.list'
  sudo apt-get update
```

## Steps to install the brain software in the deployment location on the BBB:
1. Clone the code into the deployment directory:
```
sudo mkdir /opt/openagbrain
cd /opt/openagbrain
git clone https://github.com/OpenAgInitiative/openag-device-software.git .
```
2. Configure the software:
```
./scripts/install.sh
./scripts/setup_python.sh
./scripts/upgrade.sh
```
3. The software is now running under the rc.local service. Check its status:
```
sudo systemctl status rc.local --no-pager
```

## Copy the BBB eMMC (operating system image) to an SD card:
 - Boot BBB normally
 - Insert blank 8G SD card
 - SSH into BBB
 - Run flasher script on BBB
   ```
   sudo /opt/scripts/tools/eMMC/beaglebone-black-make-microSD-flasher-from-eMMC.sh
   ```
 - Wait for script to finish and BBB LEDs to turn off
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
