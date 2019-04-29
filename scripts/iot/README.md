# How to develop / debug / test the IoT code locally

- Develop this application on OSX/Linux, instead of a beaglebone or raspi for speed and convenience.

- Run (and understand) the firebase cloud function service locally. 

- Run (and understand) the MQTT pub-sub message service locally (subscribing to a test pub-sub topic).

- Run this device application in simulation mode with a minimal device config (perhaps just a camera peripheral configured if you are testing images / uploads).  The publish to a test topic script runs has the device publish to a special pub-sub topic that is only read by the local server (above) for testing.
  - Modify line 331 to use the local firebase service URL in: `openag-device-software/device/iot/pubsub.py`

- If you are testing images, you can use the device UI with a camera peripheral to 'capture' a fake image in simulation mode.  Just go to the Peripherals page and click capture on the camera.


# How to run locally to test image uploads:
1. Run firebase cloud function service in a terminal: 
`~/openag-cloud-v1/backend-iot-firebase-function-service (img_post)> ./run_locally.sh`

2. Run MQTT service in a terminal:
`~/openag-cloud-v1/MqttToBigQuery-AppEngineFlexVM (img_post)> ./run_locally_on_test_topic.sh`

3. Make sure the brain is set to call the LOCAL URL for the firebase cloud function, check pubsub.py.

4. Make sure you brain is REGISTERED with a cloud user account.

5. Run the brain in test topic publish mode:
`~/openag-device-software (img_post)> ./scripts/iot/publish_to_test_topic.sh`

6. Copy an image into `~/openag-device-software/data/images` and wait 5 min for the brain to pick it up.
`cp ~/openag-device-software/device/peripherals/modules/usb_camera/tests/simulation_image.png ~/openag-device-software/data/images/2019-04-10-T00-00-00Z_Camera-Top.png`

7. Watch the debug output of MQTT, then go check the two storage buckets and firestore doc db.



