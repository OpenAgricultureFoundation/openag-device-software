# Installation Instructions for developing / contributing

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
./simulate.sh
```

## Next steps
See [Detailed Running Instructions](running.md)
