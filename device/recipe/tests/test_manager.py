import os
from typing import Dict, List, Union

import pytest

from app.models import RecipeModel
from device.coordinator.manager import CoordinatorManager
from device.recipe import modes
from device.recipe.manager import RecipeManager
from device.utilities.state.main import State


def make_a_state() -> State:
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
        "recipe_uuid": None,
        "start_timestamp_minutes": None,
        "last_update_minute": None,
    }
    return state


def make_a_recipe_model() -> RecipeModel:
    recipe_filename = "data/recipes/test/recipe_for_testing_do_not_modify.json"

    with open(recipe_filename, "r") as recipe_file:
        recipe_json_string = recipe_file.read()
        recipe_model = RecipeModel.objects.create(json=recipe_json_string)

    return recipe_model


def test_recipe_manager_initial_state() -> None:
    state = make_a_state()
    rm = RecipeManager(state)
    assert rm.mode == modes.INIT
    assert rm.stored_mode == None
    assert rm.recipe_uuid == None
    assert rm.recipe_name == None
    assert rm.current_timestamp_minutes != 0
    assert rm.start_timestamp_minutes == None
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


def test_recipe_manager_state_machine() -> None:
    # enable simulation mode, since our CI test systems won't have I2C
    os.environ["SIMULATE"] = "true"

    # load the test recipe file into the DB.
    cm = CoordinatorManager()
    cm.load_recipe_files()

    state = make_a_state()
    rm = RecipeManager(state)
    rm.run_init_mode()
    assert rm.mode == modes.NORECIPE

    # set a TEST recipe UUID so we have something to load
    recipe_model = make_a_recipe_model()
    rm.start_recipe(recipe_model.uuid, check_mode=False)

    rm.run_norecipe_mode()
    assert rm.mode == modes.START

    rm.run_start_mode()
    assert rm.mode == modes.QUEUED
    assert rm.recipe_uuid != None
    assert rm.start_timestamp_minutes != None

    # waits for next minute
    rm.run_queued_mode()
    assert rm.mode == modes.NORMAL

    # start normal mode and stop.
    rm.mode = modes.STOP
    rm.run_normal_mode()
    assert rm.mode == modes.STOP
    assert rm.last_update_minute == 0
    assert rm.current_phase == "p1"
    assert rm.current_cycle == "Day"
    assert rm.current_environment_name == "Day"


def test_recipe_parser_no_recipe() -> None:
    state = make_a_state()
    rm = RecipeManager(state)

    recipe_dict = {}  # type: Dict

    # should except for no recipe
    with pytest.raises(KeyError):
        transitions = rm.parse(recipe_dict)


def test_recipe_parser_minimum_recipe() -> None:
    # test a minimum recipe
    minimum_dict = {}  # type: Dict[str, Union[Dict, List]]
    minimum_dict["environments"] = {"env1": {"name": "1"}}
    minimum_dict["phases"] = [{"name": "2", "repeat": 3, "cycles": []}]
    cycle_hours = {"name": "4", "environment": "env1", "duration_hours": 5}
    cycle_mins = {"name": "4", "environment": "env1", "duration_minutes": 6}
    minimum_dict["phases"][0]["cycles"].append(cycle_hours)

    state = make_a_state()
    rm = RecipeManager(state)

    transitions = rm.parse(minimum_dict)
    hours_transitions = [
        {
            "minute": 0,
            "phase": "2",
            "cycle": "4",
            "environment_name": "1",
            "environment_state": {},
        },
        {
            "minute": 300,
            "phase": "2",
            "cycle": "4",
            "environment_name": "1",
            "environment_state": {},
        },
        {
            "minute": 600,
            "phase": "2",
            "cycle": "4",
            "environment_name": "1",
            "environment_state": {},
        },
        {
            "minute": 900,
            "phase": "End",
            "cycle": "End",
            "environment_name": "End",
            "environment_state": {},
        },
    ]
    assert transitions == hours_transitions, "Transitions do not match"

    # test an alternative cycle duration
    minimum_dict["phases"][0]["cycles"][0] = cycle_mins  # replace hours
    transitions = rm.parse(minimum_dict)
    mins_transitions = [
        {
            "minute": 0,
            "phase": "2",
            "cycle": "4",
            "environment_name": "1",
            "environment_state": {},
        },
        {
            "minute": 6,
            "phase": "2",
            "cycle": "4",
            "environment_name": "1",
            "environment_state": {},
        },
        {
            "minute": 12,
            "phase": "2",
            "cycle": "4",
            "environment_name": "1",
            "environment_state": {},
        },
        {
            "minute": 18,
            "phase": "End",
            "cycle": "End",
            "environment_name": "End",
            "environment_state": {},
        },
    ]
    assert transitions == mins_transitions, "Transitions do not match"
