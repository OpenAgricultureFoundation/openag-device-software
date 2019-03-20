# Import standard python modules
import logging, time, json, threading, os, sys, glob, uuid, jsonschema

# Import python types
from typing import Dict, List, Optional, Any, Tuple

# Import app models
from app import models

# Import device utilities
from device.utilities.statemachine.manager import StateMachineManager
from device.utilities.state.main import State
from device.utilities.communication.i2c.mux_simulator import MuxSimulator
from device.utilities.accessors import set_nested_dict_safely
from device.utilities.logger import Logger

# Import device managers
from device.recipe.manager import RecipeManager
from device.iot.manager import IotManager
from device.resource.manager import ResourceManager
from device.network.manager import NetworkManager
from device.upgrade.manager import UpgradeManager

# Import manager elements
from device.coordinator import modes, events

from django.conf import settings

# Initialize file paths
RECIPES_PATH = "data/recipes/*.json"
PERIPHERAL_SETUP_FILES_PATH = "device/peripherals/modules/*/setups/*.json"
PERIPHERAL_SETUP_SCHEMA_PATH = "data/schemas/peripheral_setup.json"
CONTROLLER_SETUP_FILES_PATH = "device/controllers/modules/*/setups/*.json"
CONTROLLER_SETUP_SCHEMA_PATH = "data/schemas/controller_setup.json"

# DEVICE_CONFIG_PATH = "data/config/device.txt"
DATA_PATH = settings.DATA_PATH  # os.getenv("STORAGE_LOCATION", "data")
DEVICE_CONFIG_PATH = DATA_PATH + "/config/device.txt"

DEVICE_CONFIG_SCHEMA_PATH = "data/schemas/device_config.json"
DEVICE_CONFIG_FILES_PATH = "data/devices/*.json"
SENSOR_VARIABLES_PATH = "data/variables/sensor_variables.json"
SENSOR_VARIABLES_SCHEMA_PATH = "data/schemas/sensor_variables.json"
ACTUATOR_VARIABLES_PATH = "data/variables/actuator_variables.json"
ACTUATOR_VARIABLES_SCHEMA_PATH = "data/schemas/actuator_variables.json"
CULTIVARS_PATH = "data/cultivations/cultivars.json"
CULTIVARS_SCHEMA_PATH = "data/schemas/cultivars.json"
CULTIVATION_METHODS_PATH = "data/cultivations/cultivation_methods.json"
CULTIVATION_METHODS_SCHEMA_PATH = "data/schemas/cultivation_methods.json"


class CoordinatorManager(StateMachineManager):
    """Manages device state machine thread that spawns child threads to run 
    recipes, read sensors, set actuators, manage control loops, sync data, 
    and manage external events."""

    # Initialize vars
    latest_publish_timestamp = 0.0
    peripherals: Dict[str, StateMachineManager] = {}
    controllers: Dict[str, StateMachineManager] = {}
    new_config: bool = False

    def __init__(self) -> None:
        """Initializes coordinator."""

        # Initialize parent class
        super().__init__()

        # Initialize logger
        self.logger = Logger("Coordinator", "coordinator")
        self.logger.debug("Initializing coordinator")

        # Initialize state
        self.state = State()

        # Initialize environment state dict, TODO: remove this
        self.state.environment = {
            "sensor": {"desired": {}, "reported": {}},
            "actuator": {"desired": {}, "reported": {}},
            "reported_sensor_stats": {
                "individual": {"instantaneous": {}, "average": {}},
                "group": {"instantaneous": {}, "average": {}},
            },
        }

        # Initialize recipe state dict, TODO: remove this
        self.state.recipe = {
            "recipe_uuid": None,
            "start_timestamp_minutes": None,
            "last_update_minute": None,
        }

        # Initialize managers
        self.recipe = RecipeManager(self.state)
        self.iot = IotManager(self.state, self.recipe)  # type: ignore
        self.resource = ResourceManager(self.state, self.iot)  # type: ignore
        self.network = NetworkManager(self.state)  # type: ignore
        self.upgrade = UpgradeManager(self.state)  # type: ignore

        # Initialize state machine transitions
        self.transitions = {
            modes.INIT: [modes.CONFIG, modes.ERROR, modes.SHUTDOWN],
            modes.CONFIG: [modes.SETUP, modes.ERROR, modes.SHUTDOWN],
            modes.SETUP: [modes.NORMAL, modes.ERROR, modes.SHUTDOWN],
            modes.NORMAL: [modes.LOAD, modes.ERROR, modes.SHUTDOWN],
            modes.LOAD: [modes.CONFIG, modes.ERROR, modes.SHUTDOWN],
            modes.RESET: [modes.INIT, modes.SHUTDOWN],
            modes.ERROR: [modes.RESET, modes.SHUTDOWN],
        }

        # Initialize state machine mode
        self.mode = modes.INIT

    @property
    def mode(self) -> str:
        """Gets mode."""
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        """Safely updates mode in state object."""
        self._mode = value
        with self.state.lock:
            self.state.device["mode"] = value

    @property
    def config_uuid(self) -> Optional[str]:
        """ Gets config uuid from shared state. """
        return self.state.device.get("config_uuid")  # type: ignore

    @config_uuid.setter
    def config_uuid(self, value: Optional[str]) -> None:
        """ Safely updates config uuid in state. """
        with self.state.lock:
            self.state.device["config_uuid"] = value

    @property
    def config_dict(self) -> Dict[str, Any]:
        """Gets config dict for config uuid in device config table."""
        if self.config_uuid == None:
            return {}
        config = models.DeviceConfigModel.objects.get(uuid=self.config_uuid)
        return json.loads(config.json)  # type: ignore

    @property
    def latest_environment_timestamp(self) -> float:
        """Gets latest environment timestamp from environment table."""
        if not models.EnvironmentModel.objects.all():
            return 0.0
        else:
            environment = models.EnvironmentModel.objects.latest()
            return float(environment.timestamp.timestamp())

    @property
    def manager_modes(self) -> Dict[str, str]:
        """Gets manager modes."""
        self.logger.debug("Getting manager modes")

        # Get known manager modes
        modes = {
            "Coordinator": self.mode,
            "Recipe": self.recipe.mode,
            "Network": self.network.mode,
            "IoT": self.iot.mode,
            "Resource": self.resource.mode,
        }

        # Get peripheral manager modes
        for peripheral_name, peripheral_manager in self.peripherals.items():
            modes[peripheral_name] = peripheral_manager.mode

        # Get controller manager modes
        for controller_name, controller_manager in self.controllers.items():
            modes[controller_name] = controller_manager.mode

        # Return modes
        self.logger.debug("Returning modes: {}".format(modes))
        return modes

    @property
    def manager_healths(self) -> Dict[str, str]:
        """Gets manager healths."""
        self.logger.debug("Getting manager healths")

        # Initialize healths
        healths = {}

        # Get peripheral manager modes
        for peripheral_name, peripheral_manager in self.peripherals.items():
            healths[peripheral_name] = peripheral_manager.health  # type: ignore

        # Return modes
        self.logger.debug("Returning healths: {}".format(healths))
        return healths

    ##### STATE MACHINE FUNCTIONS ######################################################

    def run(self) -> None:
        """Runs device state machine."""

        # Loop forever
        while True:

            # Check if thread is shutdown
            if self.is_shutdown:
                break

            # Check for transitions
            if self.mode == modes.INIT:
                self.run_init_mode()
            elif self.mode == modes.CONFIG:
                self.run_config_mode()
            elif self.mode == modes.SETUP:
                self.run_setup_mode()
            elif self.mode == modes.NORMAL:
                self.run_normal_mode()
            elif self.mode == modes.LOAD:
                self.run_load_mode()
            elif self.mode == modes.ERROR:
                self.run_error_mode()
            elif self.mode == modes.RESET:
                self.run_reset_mode()
            elif self.mode == modes.SHUTDOWN:
                self.run_shutdown_mode()
            else:
                self.logger.critical("Invalid state machine mode")
                self.mode = modes.INVALID
                self.is_shutdown = True
                break

    def run_init_mode(self) -> None:
        """Runs init mode. Loads local data files and stored database state 
        then transitions to config mode."""
        self.logger.info("Entered INIT")

        # Load local data files and stored db state
        self.load_local_data_files()
        self.load_database_stored_state()

        # Transition to config mode on next state machine update
        self.mode = modes.CONFIG

    def run_config_mode(self) -> None:
        """Runs configuration mode. If device config is not set, loads 'unspecified' 
        config then transitions to setup mode."""
        self.logger.info("Entered CONFIG")

        # Check device config specifier file exists in repo
        try:
            with open(DEVICE_CONFIG_PATH) as f:
                config_name = f.readline().strip()
        except:
            message = "Unable to read {}, using unspecified config".format(
                DEVICE_CONFIG_PATH
            )
            self.logger.warning(message)
            config_name = "unspecified"

            # Create the directories if needed
            os.makedirs(os.path.dirname(DEVICE_CONFIG_PATH), exist_ok=True)

            # Write `unspecified` to device.txt
            with open(DEVICE_CONFIG_PATH, "w") as f:
                f.write("{}\n".format(config_name))

        # Load device config
        self.logger.debug("Loading device config file: {}".format(config_name))
        device_config = json.load(open("data/devices/{}.json".format(config_name)))

        # Check if config uuid changed, if so, adjust state
        if self.config_uuid != device_config["uuid"]:
            with self.state.lock:
                self.state.peripherals = {}
                self.state.controllers = {}
                set_nested_dict_safely(
                    self.state.environment,
                    ["reported_sensor_stats"],
                    {},
                    self.state.lock,
                )
                set_nested_dict_safely(
                    self.state.environment, ["sensor", "reported"], {}, self.state.lock
                )
                self.config_uuid = device_config["uuid"]

        # Transition to setup mode on next state machine update
        self.mode = modes.SETUP

    def run_setup_mode(self) -> None:
        """Runs setup mode. Creates and spawns recipe, peripheral, and 
        controller threads, waits for all threads to initialize then 
        transitions to normal mode."""
        self.logger.info("Entered SETUP")
        config_uuid = self.state.device["config_uuid"]

        # Spawn managers
        if not self.new_config:
            self.recipe.spawn()
            self.iot.spawn()
            self.resource.spawn()
            self.network.spawn()
            self.upgrade.spawn()

        # Create and spawn peripherals
        self.logger.debug("Creating and spawning peripherals")
        self.create_peripherals()
        self.spawn_peripherals()

        # Create and spawn controllers
        self.create_controllers()
        self.spawn_controllers()

        # Wait for all threads to initialize
        while not self.all_managers_initialized():
            time.sleep(0.2)

        # Unset new config flag
        self.new_config = False

        # Transition to normal mode on next state machine update
        self.mode = modes.NORMAL

    def run_normal_mode(self) -> None:
        """Runs normal operation mode. Updates device state summary and stores device 
        state in database, checks for new events and transitions."""
        self.logger.info("Entered NORMAL")

        while True:
            # Overwrite system state in database every 100ms
            self.update_state()

            # Store environment state in every 10 minutes
            if time.time() - self.latest_environment_timestamp > 60 * 10:
                self.store_environment()

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.NORMAL):
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_load_mode(self) -> None:
        """Runs load mode, shutsdown peripheral and controller threads then transitions 
        to config mode."""
        self.logger.info("Entered LOAD")

        # Shutdown peripherals and controllers
        self.shutdown_peripheral_threads()
        self.shutdown_controller_threads()

        # Initialize timeout parameters
        timeout = 10
        start_time = time.time()

        # Loop forever
        while True:

            # Check if peripherals and controllers are shutdown
            if self.all_peripherals_shutdown() and self.all_controllers_shutdown():
                self.logger.debug("All peripherals and controllers shutdown")
                break

            # Check for timeout
            if time.time() - start_time > timeout:
                self.logger.critical("Config threads did not shutdown")
                self.mode = modes.ERROR
                return

            # Update every 100ms
            time.sleep(0.1)

        # Set new config flag
        self.new_config = True

        # Transition to config mode on next state machine update
        self.mode = modes.CONFIG

    def run_reset_mode(self) -> None:
        """Runs reset mode. Shutsdown child threads then transitions to init."""
        self.logger.info("Entered RESET")

        # Shutdown managers
        self.shutdown_peripheral_threads()
        self.shutdown_controller_threads()
        self.recipe.shutdown()
        self.iot.shutdown()

        # Transition to init mode on next state machine update
        self.mode = modes.INIT

    def run_error_mode(self) -> None:
        """Runs error mode. Shutsdown child threads, waits for new events 
        and transitions."""
        self.logger.info("Entered ERROR")

        # Shutsdown peripheral and controller threads
        self.shutdown_peripheral_threads()
        self.shutdown_controller_threads()

        # Loop forever
        while True:

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.ERROR):
                break

            # Update every 100ms
            time.sleep(0.1)

    ##### SUPPORT FUNCTIONS ############################################################

    def update_state(self) -> None:
        """Updates stored state in database. If state does not exist, creates it."""

        # TODO: Move this to state manager

        if not models.StateModel.objects.filter(pk=1).exists():
            models.StateModel.objects.create(
                id=1,
                device=json.dumps(self.state.device),
                recipe=json.dumps(self.state.recipe),
                environment=json.dumps(self.state.environment),
                peripherals=json.dumps(self.state.peripherals),
                controllers=json.dumps(self.state.controllers),
                iot=json.dumps(self.state.iot),
                resource=json.dumps(self.state.resource),
                connect=json.dumps(self.state.network),
                upgrade=json.dumps(self.state.upgrade),
            )
        else:
            models.StateModel.objects.filter(pk=1).update(
                device=json.dumps(self.state.device),
                recipe=json.dumps(self.state.recipe),
                environment=json.dumps(self.state.environment),
                peripherals=json.dumps(self.state.peripherals),
                controllers=json.dumps(self.state.controllers),
                iot=json.dumps(self.state.iot),
                resource=json.dumps(self.state.resource),
                connect=json.dumps(self.state.network),  # TODO: migrate this
                upgrade=json.dumps(self.state.upgrade),
            )

    def load_local_data_files(self) -> None:
        """ Loads local data files. """
        self.logger.info("Loading local data files")

        # Load files with no verification dependencies first
        self.load_sensor_variables_file()
        self.load_actuator_variables_file()
        self.load_cultivars_file()
        self.load_cultivation_methods_file()

        # Load recipe files after sensor/actuator variables, cultivars, and
        # cultivation methods since verification depends on them
        self.load_recipe_files()

        # Load peripheral setup files after sensor/actuator variable since verification
        # depends on them
        self.load_peripheral_setup_files()

        # Load controller setup files after sensor/actuator variable since verification
        # depends on them
        self.load_controller_setup_files()

        # Load device config after peripheral setups since verification
        # depends on  them
        self.load_device_config_files()

    def load_sensor_variables_file(self) -> None:
        """ Loads sensor variables file into database after removing all 
            existing entries. """
        self.logger.debug("Loading sensor variables file")

        # Load sensor variables and schema
        sensor_variables = json.load(open(SENSOR_VARIABLES_PATH))
        sensor_variables_schema = json.load(open(SENSOR_VARIABLES_SCHEMA_PATH))

        # Validate sensor variables with schema
        jsonschema.validate(sensor_variables, sensor_variables_schema)

        # Delete sensor variables tables
        models.SensorVariableModel.objects.all().delete()

        # Create sensor variables table
        for sensor_variable in sensor_variables:
            models.SensorVariableModel.objects.create(json=json.dumps(sensor_variable))

    def load_actuator_variables_file(self) -> None:
        """ Loads actuator variables file into database after removing all 
            existing entries. """
        self.logger.debug("Loading actuator variables file")

        # Load actuator variables and schema
        actuator_variables = json.load(open(ACTUATOR_VARIABLES_PATH))
        actuator_variables_schema = json.load(open(ACTUATOR_VARIABLES_SCHEMA_PATH))

        # Validate actuator variables with schema
        jsonschema.validate(actuator_variables, actuator_variables_schema)

        # Delete actuator variables tables
        models.ActuatorVariableModel.objects.all().delete()

        # Create actuator variables table
        for actuator_variable in actuator_variables:
            models.ActuatorVariableModel.objects.create(
                json=json.dumps(actuator_variable)
            )

    def load_cultivars_file(self) -> None:
        """ Loads cultivars file into database after removing all 
            existing entries."""
        self.logger.debug("Loading cultivars file")

        # Load cultivars and schema
        cultivars = json.load(open(CULTIVARS_PATH))
        cultivars_schema = json.load(open(CULTIVARS_SCHEMA_PATH))

        # Validate cultivars with schema
        jsonschema.validate(cultivars, cultivars_schema)

        # Delete cultivars tables
        models.CultivarModel.objects.all().delete()

        # Create cultivars table
        for cultivar in cultivars:
            models.CultivarModel.objects.create(json=json.dumps(cultivar))

    def load_cultivation_methods_file(self) -> None:
        """ Loads cultivation methods file into database after removing all 
            existing entries. """
        self.logger.debug("Loading cultivation methods file")

        # Load cultivation methods and schema
        cultivation_methods = json.load(open(CULTIVATION_METHODS_PATH))
        cultivation_methods_schema = json.load(open(CULTIVATION_METHODS_SCHEMA_PATH))

        # Validate cultivation methods with schema
        jsonschema.validate(cultivation_methods, cultivation_methods_schema)

        # Delete cultivation methods tables
        models.CultivationMethodModel.objects.all().delete()

        # Create cultivation methods table
        for cultivation_method in cultivation_methods:
            models.CultivationMethodModel.objects.create(
                json=json.dumps(cultivation_method)
            )

    def load_recipe_files(self) -> None:
        """Loads recipe files into database via recipe manager create or update 
        function."""
        self.logger.debug("Loading recipe files")

        # Get recipes
        for filepath in glob.glob(RECIPES_PATH):
            self.logger.debug("Loading recipe file: {}".format(filepath))
            with open(filepath, "r") as f:
                json_ = f.read().replace("\n", "")
                message, code = self.recipe.create_or_update_recipe(json_)
                if code != 200:
                    filename = filepath.split("/")[-1]
                    error = "Unable to load {} -> {}".format(filename, message)
                    self.logger.error(error)

    def load_peripheral_setup_files(self) -> None:
        """Loads peripheral setup files from codebase into database by creating new 
        entries after deleting existing entries. Verification depends on sensor and 
        actuator variables."""
        self.logger.info("Loading peripheral setup files")

        # Get peripheral setups
        peripheral_setups = []
        for filepath in glob.glob(PERIPHERAL_SETUP_FILES_PATH):
            self.logger.debug("Loading peripheral setup file: {}".format(filepath))
            peripheral_setups.append(json.load(open(filepath)))

        # Get get peripheral setup schema
        # TODO: Finish schema
        peripheral_setup_schema = json.load(open(PERIPHERAL_SETUP_SCHEMA_PATH))

        # Validate peripheral setups with schema
        for peripheral_setup in peripheral_setups:
            jsonschema.validate(peripheral_setup, peripheral_setup_schema)

        # Delete all peripheral setup entries from database
        models.PeripheralSetupModel.objects.all().delete()

        # TODO: Validate peripheral setup variables with database variables

        # Create peripheral setup entries in database
        for peripheral_setup in peripheral_setups:
            models.PeripheralSetupModel.objects.create(
                json=json.dumps(peripheral_setup)
            )

    def load_controller_setup_files(self) -> None:
        """Loads controller setup files from codebase into database by creating new 
        entries after deleting existing entries. Verification depends on sensor and 
        actuator variables."""
        self.logger.info("Loading controller setup files")

        # Get controller setups
        controller_setups = []
        for filepath in glob.glob(CONTROLLER_SETUP_FILES_PATH):
            self.logger.debug("Loading controller setup file: {}".format(filepath))
            controller_setups.append(json.load(open(filepath)))

        # Get get controller setup schema
        controller_setup_schema = json.load(open(CONTROLLER_SETUP_SCHEMA_PATH))

        # Validate peripheral setups with schema
        for controller_setup in controller_setups:
            jsonschema.validate(controller_setup, controller_setup_schema)

        # Delete all peripheral setup entries from database
        models.ControllerSetupModel.objects.all().delete()

        # TODO: Validate controller setup variables with database variables

        # Create peripheral setup entries in database
        for controller_setup in controller_setups:
            models.ControllerSetupModel.objects.create(
                json=json.dumps(controller_setup)
            )

    def load_device_config_files(self) -> None:
        """Loads device config files from codebase into database by creating new entries 
        after deleting existing entries. Verification depends on peripheral setups. """
        self.logger.info("Loading device config files")

        # Get devices
        device_configs = []
        for filepath in glob.glob(DEVICE_CONFIG_FILES_PATH):
            self.logger.debug("Loading device config file: {}".format(filepath))
            device_configs.append(json.load(open(filepath)))

        # Get get device config schema
        # TODO: Finish schema (see optional objects)
        device_config_schema = json.load(open(DEVICE_CONFIG_SCHEMA_PATH))

        # Validate device configs with schema
        for device_config in device_configs:
            jsonschema.validate(device_config, device_config_schema)

        # TODO: Validate device config with peripherals
        # TODO: Validate device config with varibles

        # Delete all device config entries from database
        models.DeviceConfigModel.objects.all().delete()

        # Create device config entry if new or update existing
        for device_config in device_configs:
            models.DeviceConfigModel.objects.create(json=json.dumps(device_config))

    def load_database_stored_state(self) -> None:
        """ Loads stored state from database if it exists. """
        self.logger.info("Loading database stored state")

        # Get stored state from database
        if not models.StateModel.objects.filter(pk=1).exists():
            self.logger.info("No stored state in database")
            self.config_uuid = None
            return
        stored_state = models.StateModel.objects.filter(pk=1).first()

        # Load device state
        stored_device_state = json.loads(stored_state.device)

        # Load recipe state
        stored_recipe_state = json.loads(stored_state.recipe)
        self.recipe.recipe_uuid = stored_recipe_state["recipe_uuid"]
        self.recipe.recipe_name = stored_recipe_state["recipe_name"]
        self.recipe.duration_minutes = stored_recipe_state["duration_minutes"]
        self.recipe.start_timestamp_minutes = stored_recipe_state[
            "start_timestamp_minutes"
        ]
        self.recipe.last_update_minute = stored_recipe_state["last_update_minute"]
        self.recipe.stored_mode = stored_recipe_state["mode"]

        # Load peripherals state
        stored_peripherals_state = json.loads(stored_state.peripherals)
        for peripheral_name in stored_peripherals_state:
            self.state.peripherals[peripheral_name] = {}
            if "stored" in stored_peripherals_state[peripheral_name]:
                stored = stored_peripherals_state[peripheral_name]["stored"]
                self.state.peripherals[peripheral_name]["stored"] = stored

        # Load controllers state
        stored_controllers_state = json.loads(stored_state.controllers)
        for controller_name in stored_controllers_state:
            self.state.controllers[controller_name] = {}
            if "stored" in stored_controllers_state[controller_name]:
                stored = stored_controllers_state[controller_name]["stored"]
                self.state.controllers[controller_name]["stored"] = stored

        # Load iot state
        stored_iot_state = json.loads(stored_state.iot)
        self.state.iot["stored"] = stored_iot_state.get("stored", {})

    def store_environment(self) -> None:
        """ Stores current environment state in environment table. """
        models.EnvironmentModel.objects.create(state=self.state.environment)

    def create_peripherals(self) -> None:
        """ Creates peripheral managers. """
        self.logger.info("Creating peripheral managers")

        # Verify peripherals are configured
        if self.config_dict.get("peripherals") == None:
            self.logger.info("No peripherals configured")
            return

        # Set var type
        mux_simulator: Optional[MuxSimulator]

        # Inintilize simulation parameters
        if os.environ.get("SIMULATE") == "true":
            simulate = True
            mux_simulator = MuxSimulator()
        else:
            simulate = False
            mux_simulator = None

        # Create thread locks
        i2c_lock = threading.RLock()

        # Create peripheral managers
        self.peripherals = {}
        peripheral_config_dicts = self.config_dict.get("peripherals", {})
        for peripheral_config_dict in peripheral_config_dicts:
            self.logger.debug("Creating {}".format(peripheral_config_dict["name"]))

            # Get peripheral setup dict
            peripheral_uuid = peripheral_config_dict["uuid"]
            peripheral_setup_dict = self.get_peripheral_setup_dict(peripheral_uuid)

            # Verify valid peripheral config dict
            if peripheral_setup_dict == {}:
                self.logger.critical(
                    "Invalid peripheral uuid in device "
                    "config. Validator should have caught this."
                )
                continue

            # Get peripheral module and class name
            module_name = (
                "device.peripherals.modules." + peripheral_setup_dict["module_name"]
            )
            class_name = peripheral_setup_dict["class_name"]

            # Import peripheral library
            module_instance = __import__(module_name, fromlist=[class_name])
            class_instance = getattr(module_instance, class_name)

            # Create peripheral manager
            peripheral_name = peripheral_config_dict["name"]

            peripheral = class_instance(
                name=peripheral_name,
                state=self.state,
                config=peripheral_config_dict,
                simulate=simulate,
                i2c_lock=i2c_lock,
                mux_simulator=mux_simulator,
            )
            self.peripherals[peripheral_name] = peripheral

    def get_peripheral_setup_dict(self, uuid: str) -> Dict[str, Any]:
        """Gets peripheral setup dict for uuid in peripheral setup table."""
        if not models.PeripheralSetupModel.objects.filter(uuid=uuid).exists():
            return {}
        else:
            json_ = models.PeripheralSetupModel.objects.get(uuid=uuid).json
        peripheral_setup_dict = json.loads(json_)
        return peripheral_setup_dict  # type: ignore

    def get_controller_setup_dict(self, uuid: str) -> Dict[str, Any]:
        """Gets controller setup dict for uuid in peripheral setup table."""
        if not models.ControllerSetupModel.objects.filter(uuid=uuid).exists():
            return {}
        else:
            json_ = models.ControllerSetupModel.objects.get(uuid=uuid).json
        controller_setup_dict = json.loads(json_)
        return controller_setup_dict  # type: ignore

    def spawn_peripherals(self) -> None:
        """ Spawns peripherals. """
        if self.peripherals == {}:
            self.logger.info("No peripheral threads to spawn")
        else:
            self.logger.info("Spawning peripherals")
            for name, manager in self.peripherals.items():
                manager.spawn()

    def create_controllers(self) -> None:
        """ Creates controller managers. """
        self.logger.info("Creating controller managers")

        # Verify controllers are configured
        if self.config_dict.get("controllers") == None:
            self.logger.info("No controllers configured")
            return

        # Create controller managers
        self.controllers = {}
        controller_config_dicts = self.config_dict.get("controllers", {})
        for controller_config_dict in controller_config_dicts:
            self.logger.debug("Creating {}".format(controller_config_dict["name"]))

            # Get controller setup dict
            controller_uuid = controller_config_dict["uuid"]
            controller_setup_dict = self.get_controller_setup_dict(controller_uuid)

            # Verify valid controller config dict
            if controller_setup_dict == None:
                self.logger.critical(
                    "Invalid controller uuid in device "
                    "config. Validator should have caught this."
                )
                continue

            # Get controller module and class name
            module_name = (
                "device.controllers.modules." + controller_setup_dict["module_name"]
            )
            class_name = controller_setup_dict["class_name"]

            # Import controller library
            module_instance = __import__(module_name, fromlist=[class_name])
            class_instance = getattr(module_instance, class_name)

            # Create controller manager
            controller_name = controller_config_dict["name"]
            controller_manager = class_instance(
                controller_name, self.state, controller_config_dict
            )
            self.controllers[controller_name] = controller_manager

    def spawn_controllers(self) -> None:
        """ Spawns controllers. """
        if self.controllers == {}:
            self.logger.info("No controller threads to spawn")
        else:
            self.logger.info("Spawning controllers")
            for name, manager in self.controllers.items():
                self.logger.debug("Spawning {}".format(name))
                manager.spawn()

    def all_managers_initialized(self) -> bool:
        """Checks if all managers have initialized."""
        if self.recipe.mode == modes.INIT:
            return False
        elif not self.all_peripherals_initialized():
            return False
        elif not self.all_controllers_initialized():
            return False
        return True

    def all_peripherals_initialized(self) -> bool:
        """Checks if all peripherals have initialized."""
        for name, manager in self.peripherals.items():
            if manager.mode == modes.INIT:
                return False
        return True

    def all_controllers_initialized(self) -> bool:
        """Checks if all controllers have initialized."""
        for name, manager in self.controllers.items():
            if manager.mode == modes.INIT:
                return False
        return True

    def shutdown_peripheral_threads(self) -> None:
        """Shutsdown all peripheral threads."""
        for name, manager in self.peripherals.items():
            manager.shutdown()

    def shutdown_controller_threads(self) -> None:
        """Shutsdown all controller threads."""
        for name, manager in self.controllers.items():
            manager.shutdown()

    def all_peripherals_shutdown(self) -> bool:
        """Check if all peripherals are shutdown."""
        for name, manager in self.peripherals.items():
            if manager.thread.is_alive():
                return False
        return True

    def all_controllers_shutdown(self) -> bool:
        """Check if all controllers are shutdown."""
        for name, manager in self.controllers.items():
            if manager.thread.is_alive():
                return False
        return True

    ##### EVENT FUNCTIONS ##############################################################

    def check_events(self) -> None:
        """Checks for a new event. Only processes one event per call, even if there are
        multiple in the queue. Events are processed first-in-first-out (FIFO)."""

        # Check for new events
        if self.event_queue.empty():
            return

        # Get request
        request = self.event_queue.get()
        self.logger.debug("Received new request: {}".format(request))

        # Get request parameters
        try:
            type_ = request["type"]
        except KeyError as e:
            message = "Invalid request parameters: {}".format(e)
            self.logger.exception(message)
            return

        # Execute request
        if type_ == events.RESET:
            self._reset()  # Defined in parent class
        elif type_ == events.SHUTDOWN:
            self._shutdown()  # Defined in parent class
        elif type_ == events.LOAD_DEVICE_CONFIG:
            self._load_device_config(request)
        else:
            self.logger.error("Invalid event request type in queue: {}".format(type_))

    def load_device_config(self, uuid: str) -> Tuple[str, int]:
        """Pre-processes load device config event request."""
        self.logger.debug("Pre-processing load device config request")

        # Get filename of corresponding uuid
        filename = None
        for filepath in glob.glob(DEVICE_CONFIG_FILES_PATH):
            self.logger.debug(filepath)
            device_config = json.load(open(filepath))
            if device_config["uuid"] == uuid:
                filename = filepath.split("/")[-1].replace(".json", "")

        # Verify valid config uuid
        if filename == None:
            message = "Invalid config uuid, corresponding filepath not found"
            self.logger.debug(message)
            return message, 400

        # Check valid mode transition if enabled
        if not self.valid_transition(self.mode, modes.LOAD):
            message = "Unable to load device config from {} mode".format(self.mode)
            self.logger.debug(message)
            return message, 400

        # Add load device config event request to event queue
        request = {"type": events.LOAD_DEVICE_CONFIG, "filename": filename}
        self.event_queue.put(request)

        # Successfully added load device config request to event queue
        message = "Loading config"
        return message, 200

    def _load_device_config(self, request: Dict[str, Any]) -> None:
        """Processes load device config event request."""
        self.logger.debug("Processing load device config request")

        # Get request parameters
        filename = request.get("filename")

        # Write config filename to device config path
        with open(DEVICE_CONFIG_PATH, "w") as f:
            f.write(str(filename) + "\n")

        # Transition to init mode on next state machine update
        self.mode = modes.LOAD
