# Detailed Running Instructions

## Stopping the brain when it is run from /etc/rc.local
```
sudo service rc.local stop
systemctl status rc-local.service
```

## Directly run the brain on the beaglebone for developing (see note below if on other platforms)
```
./run.sh
```

## If you are not on a beaglebone, you may want simulate the I2C bus.  (if you are on Linux or OSX doing development).  Use this command in place of the one above.
```
./simulation.sh
```

## Next steps
See [Contributing](contributing.md)
