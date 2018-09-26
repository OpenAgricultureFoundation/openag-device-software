# Import standard python libraries
import os, sys, json, pytest, time

# Set system path and directory
root_dir = os.environ["OPENAG_BRAIN_ROOT"]
sys.path.append(root_dir)
os.chdir(root_dir)

# Import the IoT communications class
from device.iot.pubsub import IoTPubSub


# Callback passed into IoTPubSub, that does nothing
def dummy_command_received(command, arg0, arg1):
    pass


# def test_send_image():

#     path = "device/iot/tests/webcam-1-test.png"  # 344K (message limit is 256K)
#     f = open(path, "rb")
#     contents_bytes = f.read()
#     f.close()

#     state_dict = {}
#     ps = IoTPubSub(dummy_command_received, state_dict)
#     ps.process_network_events()

#     ps.publishBinaryImage("webcam-top", "png", contents_bytes)
#     count = 0
#     while 0 == ps.publishCount and count < 20:
#         count = count + 1
#         ps.process_network_events()
#         time.sleep(1)
#         print("IoTPubSub.publishCount={}".format(ps.publishCount))
#     assert ps.publishCount != 0
