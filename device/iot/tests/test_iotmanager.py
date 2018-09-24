import pytest, os, time

# Import the IoT manager class
from iot.iot_manager import IoTManager
from device.state.main import State


# Need a mock class to pass into the IoTManager, which makes calls to it.
class MockDeviceManager:
    # Initialize environment state dict
    state = State()
    state.environment = {
        "sensor": {"desired": {}, "reported": {}},
        "actuator": {"desired": {}, "reported": {}},
        "reported_sensor_stats": {
            "individual": {
                "instantaneous": {"test_var": '{"name":"pytest"}'}, "average": {}
            },
            "group": {"instantaneous": {}, "average": {}},
        },
    }
    load_recipe_json_called = False
    process_start_recipe_event_called = False
    process_stop_recipe_event_called = False

    def load_recipe_json(recipe_json):
        load_recipe_json_called = True

    def process_start_recipe_event(recipe_uuid):
        process_start_recipe_event_called = True

    def process_stop_recipe_event():
        process_stop_recipe_event_called = True


@pytest.mark.skip(reason="Not implemented yet")
def test_iot_manager():
    assert False, "debugrob, fix this test, not working"
    mdm = MockDeviceManager()
    ps = IoTManager(mdm.state, mdm)
    ps.spawn()
    time.sleep(2)
    ps.publish()
    time.sleep(2)
    ps.stop()
    count = 0
    while not ps.stopped() and count < 20:
        count = count + 1
        time.sleep(1)
    time.sleep(2)
    assert ps.stopped()
