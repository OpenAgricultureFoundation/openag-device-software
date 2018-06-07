import pytest, os
from device.managers.device import DeviceManager
from device.utilities.modes import Modes
from device.utilities.errors import Errors


def test_device_manager_initial_state():
    dm = DeviceManager()
    assert dm.mode == Modes.INIT
    assert dm.error == Errors.NONE
    assert dm.commanded_mode == None
    assert dm.request == None
    assert dm.response == None
    assert dm.config_uuid == None
    assert dm.commanded_config_uuid == None
    assert dm.config_dict == None
    assert dm.latest_environment_timestamp == 0
    assert dm.all_threads_initialized() == False
    assert dm.all_peripherals_initialized() == True # no perips to init is OK
    assert dm.all_controllers_initialized() == True # no contr to init is OK


def test_device_manager_state_machine():
    # enable simulation mode, since our CI test systems won't have I2C 
    os.environ['SIMULATE'] = "true"

    dm = DeviceManager()
    dm.run_init_mode()
    assert dm.mode == Modes.CONFIG

    dm.run_config_mode()
    assert dm.mode == Modes.SETUP

#debugrob: TODO code needs to handle simulated more, or fix the perip/cont init modes
    # this waits forever for (simulated) peripherals to initialize
#    dm.run_setup_mode()
#    assert dm.mode == Modes.NORMAL
#    assert dm.all_threads_initialized() == True
    
    #debugrob, is this the only way to stop?   Why is Modes.STOP not handled?
#    dm.mode( Modes.ERROR )
#    dm.run_normal_mode()

#    dm.run_error_mode()
#    dm.mode( Modes.RESET )

#    dm.run_reset_mode()
#    assert dm.mode == Modes.INIT


@pytest.mark.skip(reason="Not implemented yet")
def test_device_manager_state_machine():
    dm = DeviceManager()
    dm.run_state_machine()
    assert False, "debugrob, write these tests"



