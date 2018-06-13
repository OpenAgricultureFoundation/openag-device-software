import pytest, os, time


# Import the IoT communications class
from iot.iot_pubsub import IoTPubSub


# Callback passed into IoTPubSub, that does nothing
def dummy_command_received( command, arg0, arg1 ):
    pass


def test_send_image():

    path = 'tests/iot/webcam-1-test.png' # 344K (message limit is 256K)
    f = open( path, 'rb' )
    contents_bytes = f.read()
    f.close()

    ps = IoTPubSub( dummy_command_received ) 
    ps.process_network_events() 

    ps.publishBinaryImage( 'webcam-top', contents_bytes ) 
    count = 0
    while 0 == ps.publishCount and count < 20:
        count = count + 1
        ps.process_network_events() 
        time.sleep(1)
        print('IoTPubSub.publishCount={}'.format(ps.publishCount))
    assert ps.publishCount != 0
    
