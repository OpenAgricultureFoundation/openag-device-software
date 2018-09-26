import pytest, os, time


# Import the IoT communications class
from device.iot.pubsub import IoTPubSub


# # Callback passed into IoTPubSub, called when we receive a command.
# def live_command_received(command, arg0, arg1):
#     # When live, we have no idea what message we will get (normally resends
#     # of previous messages).
#     assert command != None
#     print("IoTPubSub.live_command_received")


# def test_pubsub_initial_state():
#     state_dict = {}
#     ps = IoTPubSub(live_command_received, state_dict)
#     assert ps.lastConfigVersion == 0
#     ps.lastConfigVersion = 123
#     assert ps.lastConfigVersion == 123
#     assert ps.connected == False
#     assert ps.messageCount == 0
#     assert ps.publishCount == 0
#     # we don't process network events here, so we won't get any messages.


# def test_pubsub_live_recv_cmd():
#     state_dict = {}
#     ps = IoTPubSub(live_command_received, state_dict)
#     count = 0
#     while not ps.connected and count < 20:
#         count = count + 1
#         ps.process_network_events()
#         time.sleep(1)
#         print("IoTPubSub.connected={}".format(ps.connected))
#     assert ps.connected == True
#     count = 0
#     while 0 == ps.messageCount and count < 20:
#         count = count + 1
#         ps.process_network_events()
#         time.sleep(1)
#         print("IoTPubSub.messageCount={}".format(ps.messageCount))
#     assert ps.messageCount != 0


# def test_pubsub_publish_env_var():
#     state_dict = {}
#     ps = IoTPubSub(live_command_received, state_dict)
#     valuesDict = {}
#     value = {}
#     value["name"] = "pytest"
#     value["type"] = "string"
#     value["value"] = '{"name":"pytest"}'
#     valuesDict["values"] = [value]  # new list of one value
#     # 'pytest' is an invalid messageType, so will be dropped by MQTT server.
#     ps.publishEnvVar("pytest", valuesDict, messageType="pytest")
#     count = 0
#     while 0 == ps.publishCount and count < 20:
#         count = count + 1
#         ps.process_network_events()
#         time.sleep(1)
#         print("IoTPubSub.publishCount={}".format(ps.publishCount))
#     assert ps.publishCount != 0


# def test_pubsub_publish_command_reply():
#     state_dict = {}
#     ps = IoTPubSub(live_command_received, state_dict)
#     # this may actually make it past the MQTT server and end up in BQ:
#     ps.publishCommandReply("pytest", '{"name":"pytest"}')
#     count = 0
#     while 0 == ps.publishCount and count < 20:
#         count = count + 1
#         ps.process_network_events()
#         time.sleep(1)
#         print("IoTPubSub.publishCount={}".format(ps.publishCount))
#     assert ps.publishCount != 0
