# Installation Instructions

## For developers:

### Supported Operating Systems:
```
Currently tested:
 - Beaglebone black | Stretch IoT | Debian 9.3
 - Should work on most *nix systems (OSX and Ubuntu are our development platforms)
```

### Clone repo:
```
cd ~
git clone https://github.com/OpenAgInitiative/openag-device-software.git
```

### Go to repo directory:
```
cd ~/openag-device-software
```

### Run the scripts:
```
./scripts/install.sh
./scripts/setup_python.sh
./scripts/upgrade.sh
```

### Run the software in simulation mode (no I2C devices required):
```
sudo ./simulate.sh
```


## To just install (or upgrade to) the latest debian package:
```
sudo apt-get update
sudo apt-get install -y openagbrain
dpkg -s openagbrain
```


## Next steps
See [Detailed Running Instructions](running.md)
