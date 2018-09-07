# Part 5: User Setup

Back to [Part 4: Provision BBB](provision_bbb.md)...or...Forward to [README](../README.md)

## Connect to the Device UI
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
6. Open this [device UI link http://192.168.8.1](http://192.168.8.1) in your web brower.
	
## Initial Device UI Setup:
1. Login to the device UI with:
```
Username: openag
Password: openag
```
2. Change the password by going to `Password` tab.

## Load Device Config:
1. Look for a label on the electronics board of the device that says "CONFIG", it should look like:
	```
	CONFIG: edu-v0.3.0
	```
2. Got to `Config` tab, select your hardware config from the drop down and click the `Load Config` button.

## Connect the Device to the Internet:
1. Go to the `Connect` tab.
2. Select your wifi access point from the list and type its password, then click the `Join Wifi` button.
3. Wait a minute for the connection to complete and the page to refresh.

## Register the Device with our server:
1. Click the `Register this device` button.
2. Wait a minute for the connection to complete and the page to refresh.
3. Click the link that says: `Please click here to add this device to your OpenAg cloud user account`.
4. Log in or create an account on our cloud UI.
5. Add your device to your account.
6. Send your device a recipe to start growing a plant!



