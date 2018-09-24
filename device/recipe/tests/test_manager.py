import pytest, os
from device.managers.recipe import RecipeManager
from device.managers.device import DeviceManager
from device.utilities.modes import Modes
from device.utilities.errors import Errors
from device.state.main import State


def make_a_state():
    state = State()
    state.environment = {
        "sensor": {"desired": {}, "reported": {}},
        "actuator": {"desired": {}, "reported": {}},
        "reported_sensor_stats": {
            "individual": {"instantaneous": {}, "average": {}},
            "group": {"instantaneous": {}, "average": {}},
        },
    }
    state.recipe = {
        "recipe_uuid": None, "start_timestamp_minutes": None, "last_update_minute": None
    }
    return state


def test_recipe_manager_initial_state():
    state = make_a_state()
    rm = RecipeManager(state)
    assert rm.mode == Modes.INIT
    assert rm.error == Errors.NONE
    assert rm.commanded_mode == None
    assert rm.stored_mode == None
    assert rm.recipe_uuid == None
    assert rm.commanded_recipe_uuid == None
    assert rm.recipe_name == None
    assert rm.current_timestamp_minutes != 0
    assert rm.start_timestamp_minutes == None
    assert rm.commanded_start_timestamp_minutes == None
    assert rm.start_datestring == None
    assert rm.duration_minutes == None
    assert rm.last_update_minute == None
    assert rm.percent_complete == None
    assert rm.percent_complete_string == None
    assert rm.time_remaining_minutes == None
    assert rm.time_remaining_string == None
    assert rm.time_elapsed_string == None
    assert rm.current_phase == None
    assert rm.current_cycle == None
    assert rm.current_environment_name == None
    assert rm.current_environment_state == None


def test_recipe_manager_state_machine():
    # enable simulation mode, since our CI test systems won't have I2C
    os.environ["SIMULATE"] = "true"

    # load the test recipe file into the postgres openag_brain DB.
    dm = DeviceManager()
    dm.load_recipe_files()

    state = make_a_state()
    rm = RecipeManager(state)
    rm.run_init_mode()
    assert rm.mode == Modes.NORECIPE

    # set the start command so the no-recipe mode will move to next state
    rm.commanded_mode = Modes.START
    rm.run_norecipe_mode()
    assert rm.mode == Modes.START

    # set a TEST recipe UUID so we have something to load
    rm.commanded_recipe_uuid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    rm.run_start_mode()
    assert rm.mode == Modes.QUEUED
    assert rm.commanded_recipe_uuid == None
    assert rm.start_timestamp_minutes != None

    # waits for next minute
    rm.run_queued_mode()
    assert rm.mode == Modes.NORMAL

    # start normal mode and stop.
    rm.commanded_mode = Modes.STOP
    rm.run_normal_mode()
    assert rm.commanded_mode == Modes.NONE
    assert rm.mode == Modes.STOP
    assert rm.last_update_minute == 0
    assert rm.current_phase == "p1"
    assert rm.current_cycle == "Day"
    assert rm.current_environment_name == "Day"
