# Part 5: User Setup

Back to [Part 4: Provision BBB](provision_bbb.md)...or...Forward to [README](../README.md)

## Connect to Device UI
1. Plug in bot
2. Wait a few minutes
3. Look at label on beaglebone for wifi code (e.g. WIFI: 46D8)
4. Connect your laptop to the beaglebone wifi access point
	```
	BeagleBone-<CODE>
	```
	Example:
	```
	BeagleBone-46D8
	```
5. Enter the wifi password:
	```
	BeagleBone
	```
6. Open device UI in a web brower and navigating to:
	```
	192.168.8.1 # TODO: can we make this a more human readable name (e.g. device.ui?)
	```


## Connect Device to Internet
1. Got to `connect tab`, follow instructions to connect bot to your wifi


## Load Device Config:
1. Look at label on the Brain PCB for "CONFIG", should look like
	```
	CONFIG: edu-v0.4.0
	```
2. Got to `config tab`, select your hardware config from the drop down and click **Load** button
