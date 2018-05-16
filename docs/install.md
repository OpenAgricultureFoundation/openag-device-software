# Installation Instructions

## Device
### Get os onto device
```
Currently tested:
 - Beaglebone black | Stretch IoT | Debian 9.3
 - Should work on most *nix systems
```

### Clone repo
```
git clone https://github.com/jakerye/openag-brain-quartz.git
```

### Go to repo directory
```
cd openag-brain-quartz
```

### Run install script
```
sudo ./install.sh
```

## Create the database
```
./create_database.sh
```

## Set up a Python Environment
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
