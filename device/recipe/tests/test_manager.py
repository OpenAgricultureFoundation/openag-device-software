import pytest, os

# from device.managers.recipe import RecipeManager
# from device.managers.device import DeviceManager
# from device.utilities.modes import Modes
# from device.utilities.errors import Errors
# from device.state.main import State


# def make_a_state():
#     state = State()
#     state.environment = {
#         "sensor": {"desired": {}, "reported": {}},
#         "actuator": {"desired": {}, "reported": {}},
#         "reported_sensor_stats": {
#             "individual": {"instantaneous": {}, "average": {}},
#             "group": {"instantaneous": {}, "average": {}},
#         },
#     }
#     state.recipe = {
#         "recipe_uuid": None, "start_timestamp_minutes": None, "last_update_minute": None
#     }
#     return state


# def test_recipe_manager_initial_state():
#     state = make_a_state()
#     rm = RecipeManager(state)
#     assert rm.mode == Modes.INIT
#     assert rm.error == Errors.NONE
#     assert rm.commanded_mode == None
#     assert rm.stored_mode == None
#     assert rm.recipe_uuid == None
#     assert rm.commanded_recipe_uuid == None
#     assert rm.recipe_name == None
#     assert rm.current_timestamp_minutes != 0
#     assert rm.start_timestamp_minutes == None
#     assert rm.commanded_start_timestamp_minutes == None
#     assert rm.start_datestring == None
#     assert rm.duration_minutes == None
#     assert rm.last_update_minute == None
#     assert rm.percent_complete == None
#     assert rm.percent_complete_string == None
#     assert rm.time_remaining_minutes == None
#     assert rm.time_remaining_string == None
#     assert rm.time_elapsed_string == None
#     assert rm.current_phase == None
#     assert rm.current_cycle == None
#     assert rm.current_environment_name == None
#     assert rm.current_environment_state == None


# def test_recipe_manager_state_machine():
#     # enable simulation mode, since our CI test systems won't have I2C
#     os.environ["SIMULATE"] = "true"

#     # load the test recipe file into the postgres openag_brain DB.
#     dm = DeviceManager()
#     dm.load_recipe_files()

#     state = make_a_state()
#     rm = RecipeManager(state)
#     rm.run_init_mode()
#     assert rm.mode == Modes.NORECIPE

#     # set the start command so the no-recipe mode will move to next state
#     rm.commanded_mode = Modes.START
#     rm.run_norecipe_mode()
#     assert rm.mode == Modes.START

#     # set a TEST recipe UUID so we have something to load
#     rm.commanded_recipe_uuid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
#     rm.run_start_mode()
#     assert rm.mode == Modes.QUEUED
#     assert rm.commanded_recipe_uuid == None
#     assert rm.start_timestamp_minutes != None

#     # waits for next minute
#     rm.run_queued_mode()
#     assert rm.mode == Modes.NORMAL

#     # start normal mode and stop.
#     rm.commanded_mode = Modes.STOP
#     rm.run_normal_mode()
#     assert rm.commanded_mode == Modes.NONE
#     assert rm.mode == Modes.STOP
#     assert rm.last_update_minute == 0
#     assert rm.current_phase == "p1"
#     assert rm.current_cycle == "Day"
#     assert rm.current_environment_name == "Day"


# def test_recipe_parser_no_recipe():
#     # should except for no recipe
#     with pytest.raises(KeyError):
#         recipe_dict = {}
#         recipe_parser = RecipeParser()
#         transitions = recipe_parser.parse(recipe_dict)


# def test_recipe_parser_minimum_recipe():
#     # test a minimum recipe
#     minimum_dict = {}
#     minimum_dict["environments"] = {"env1": {"name": "1"}}
#     minimum_dict["phases"] = [{"name": "2", "repeat": 3, "cycles": []}]
#     cycle_hours = {"name": "4", "environment": "env1", "duration_hours": 5}
#     cycle_mins = {"name": "4", "environment": "env1", "duration_minutes": 6}
#     minimum_dict["phases"][0]["cycles"].append(cycle_hours)
#     recipe_parser = RecipeParser()
#     transitions = recipe_parser.parse(minimum_dict)
#     hours_transitions = [
#         {
#             "minute": 0,
#             "phase": "2",
#             "cycle": "4",
#             "environment_name": "1",
#             "environment_state": {},
#         },
#         {
#             "minute": 300,
#             "phase": "2",
#             "cycle": "4",
#             "environment_name": "1",
#             "environment_state": {},
#         },
#         {
#             "minute": 600,
#             "phase": "2",
#             "cycle": "4",
#             "environment_name": "1",
#             "environment_state": {},
#         },
#         {
#             "minute": 900,
#             "phase": "End",
#             "cycle": "End",
#             "environment_name": "End",
#             "environment_state": {},
#         },
#     ]
#     assert transitions == hours_transitions, "Transitions do not match"

#     # test an alternative cycle duration
#     minimum_dict["phases"][0]["cycles"][0] = cycle_mins  # replace hours
#     transitions = recipe_parser.parse(minimum_dict)
#     mins_transitions = [
#         {
#             "minute": 0,
#             "phase": "2",
#             "cycle": "4",
#             "environment_name": "1",
#             "environment_state": {},
#         },
#         {
#             "minute": 6,
#             "phase": "2",
#             "cycle": "4",
#             "environment_name": "1",
#             "environment_state": {},
#         },
#         {
#             "minute": 12,
#             "phase": "2",
#             "cycle": "4",
#             "environment_name": "1",
#             "environment_state": {},
#         },
#         {
#             "minute": 18,
#             "phase": "End",
#             "cycle": "End",
#             "environment_name": "End",
#             "environment_state": {},
#         },
#     ]
#     assert transitions == mins_transitions, "Transitions do not match"
