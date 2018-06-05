# Installation Instructions

## Device
### Get os onto device
```
Currently tested:
 - Beaglebone black | Stretch IoT | Debian 9.3
 - Should work on most *nix systems (OSX and Ubuntu are our development platforms)
```

### Clone repo
```
git clone https://github.com/OpenAgInitiative/openag-device-software.git
```

### Go to repo directory
```
cd openag-device-software
```

### Run install script
```
sudo ./install.sh
```

## Set up a Python Environment and create our database
```
./setup_python.sh
```

### Run software
```
./run.sh
./run.sh --simulate # to run w/simulated hardware
./run.sh --no-device # to only run app (useful to manipulate data in admin console)
```

## Next steps
See [Running Instructions](running.md)
