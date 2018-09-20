# Import python modules
import logging, time, json, threading, os, sys, glob, uuid

# Import django modules
from django.db.models.signals import post_save
from django.dispatch import receiver

# Import json validators
from jsonschema import validate

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.accessors import set_nested_dict_safely

# Import device state
from device.state.main import State

# Import device managers
from device.recipe.manager import RecipeManager
from device.event.manager import EventManager
from device.resource.manager import ResourceManager
from device.iot.manager import IoTManager
from device.connect.manager import ConnectManager
from device.upgrade.manager import UpgradeManager

# Import device simulators
from device.communication.i2c.mux_simulator import MuxSimulator

# Import database models
from app.models import (
    StateModel,
    EventModel,
    EnvironmentModel,
    SensorVariableModel,
    ActuatorVariableModel,
    CultivarModel,
    CultivationMethodModel,
    RecipeModel,
    PeripheralSetupModel,
    DeviceConfigModel,
)

# Import coordinator modules
from device.coordinator.events import CoordinatorEvents


class CoordinatorManager(CoordinatorEvents):
    """Manages device state machine thread that spawns child threads to run 
    recipes, read sensors, set actuators, manage control loops, sync data, 
    and manage external events."""

    # Initialize logger
    extra = {"console_name": "Coordinator", "file_name": "Coordinator"}
    logger = logging.getLogger("coordinator")
    logger = logging.LoggerAdapter(logger, extra)

    # Initialize device mode and error
    _mode = None

    # Initialize state object, `state` serves as shared memory between threads
    state = State()

    # Initialize environment state dict
    state.environment = {
        "sensor": {"desired": {}, "reported": {}},
        "actuator": {"desired": {}, "reported": {}},
        "reported_sensor_stats": {
            "individual": {"instantaneous": {}, "average": {}},
            "group": {"instantaneous": {}, "average": {}},
        },
    }

    # Initialize recipe state dict
    state.recipe = {
        "recipe_uuid": None, "start_timestamp_minutes": None, "last_update_minute": None
    }

    # Initialize recipe object
    recipe = RecipeManager(state)

    # Intialize event object
    event = EventManager(state)  # TODO: remove this
    # post_save.connect(event.process, sender=EventModel)

    # Initialize peripheral and controller managers
    peripherals = None
    controllers = None

    def __init__(self):
        """Initializes coordinator."""
        self.logger.debug("Initializing coordinator")

        # Initialize mode and error
        self.mode = Modes.INIT

        # Initialize latest publish timestamp
        self.latest_publish_timestamp = 0

        # Initialize managers
        self.iot = IoTManager(self.state, self.recipe)
        self.resource = ResourceManager(self.state, self, self.iot)
        self.connect = ConnectManager(self.state, self.iot)
        self.upgrade = UpgradeManager(self.state)

    @property
    def mode(self):
        """Gets mode."""
        return self._mode

    @mode.setter
    def mode(self, value):
        """Safely updates mode in state object """
        self._mode = value
        with self.state.lock:
            self.state.device["mode"] = value

    @property
    def commanded_mode(self):
        """ Gets commanded mode from shared state object. """
        if "commanded_mode" in self.state.device:
            return self.state.device["commanded_mode"]
        else:
            return None

    @commanded_mode.setter
    def commanded_mode(self, value):
        """ Safely updates commanded mode in state object. """
        with self.state.lock:
            self.state.device["commanded_mode"] = value

    @property
    def request(self):
        """ Gets request from shared state object. """
        if "request" in self.state.device:
            return self.state.device["request"]
        else:
            return None

    @request.setter
    def request(self, value):
        """ Safely updates request in state object. """
        with self.state.lock:
            self.state.device["request"] = value

    @property
    def response(self):
        """ Gets response from shared state object. """
        if "response" in self.state.device:
            return self.state.device["response"]
        else:
            return None

    @response.setter
    def response(self, value):
        """ Safely updates response in state object. """
        with self.state.lock:
            self.state.device["response"] = value

    @property
    def config_uuid(self):
        """ Gets config uuid from shared state. """
        if "config_uuid" in self.state.device:
            return self.state.device["config_uuid"]
        else:
            return None

    @config_uuid.setter
    def config_uuid(self, value):
        """ Safely updates config uuid in state. """
        with self.state.lock:
            self.state.device["config_uuid"] = value

    @property
    def commanded_config_uuid(self):
        """ Gets commanded config uuid from shared state. """
        if "commanded_config_uuid" in self.state.device:
            return self.state.device["commanded_config_uuid"]
        else:
            return None

    @commanded_config_uuid.setter
    def commanded_config_uuid(self, value):
        """Safely updates commanded config uuid in state."""
        with self.state.lock:
            self.state.device["commanded_config_uuid"] = value

    @property
    def config_dict(self):
        """Gets config dict for config uuid in device config table."""
        if self.config_uuid == None:
            return None
        config = DeviceConfigModel.objects.get(uuid=self.config_uuid)
        return json.loads(config.json)

    @property
    def latest_environment_timestamp(self):
        """Gets latest environment timestamp from environment table."""
        if not EnvironmentModel.objects.all():
            return 0
        else:
            environment = EnvironmentModel.objects.latest()
            return environment.timestamp.timestamp()

    def spawn(self, delay=None):
        """Spawns device thread."""
        self.thread = threading.Thread(target=self.run_state_machine, args=(delay,))
        self.thread.daemon = True
        self.thread.start()

    def run_state_machine(self, delay: float = 0) -> None:
        """Runs device state machine."""

        # Wait for optional delay
        time.sleep(delay)

        self.logger.info("Spawning device thread")

        # Start state machine
        self.logger.info("Started state machine")
        while True:
            if self.mode == Modes.INIT:
                self.run_init_mode()
            elif self.mode == Modes.CONFIG:
                self.run_config_mode()
            elif self.mode == Modes.SETUP:
                self.run_setup_mode()
            elif self.mode == Modes.NORMAL:
                self.run_normal_mode()
            elif self.mode == Modes.LOAD:
                self.run_load_mode()
            elif self.mode == Modes.ERROR:
                self.run_error_mode()
            elif self.mode == Modes.RESET:
                self.run_reset_mode()

    def run_init_mode(self):
        """Runs initialization mode. Loads stored state from database then 
        transitions to CONFIG."""
        self.logger.info("Entered INIT")

        # Load local data files
        self.load_local_data_files()

        # Load stored state from database
        self.load_database_stored_state()

        # Transition to CONFIG
        self.mode = Modes.CONFIG

    def run_config_mode(self):
        """Runs configuration mode. If device config is not set, waits for 
        config command then transitions to SETUP."""
        self.logger.info("Entered CONFIG")

        # Check device config specifier file exists in repo
        DEVICE_CONFIG_PATH = "data/config/device.txt"
        try:
            with open(DEVICE_CONFIG_PATH) as f:
                config_name = f.readline().strip()
        except:
            message = "Unable to read {}, using unspecified config".format(
                DEVICE_CONFIG_PATH
            )
            self.logger.warning(message)
            config_name = "unspecified"

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

        # Transition to SETUP
        self.mode = Modes.SETUP

    def run_setup_mode(self):
        """Runs setup mode. Creates and spawns recipe, peripheral, and 
        controller threads, waits for all threads to initialize then 
        transitions to NORMAL."""
        self.logger.info("Entered SETUP")
        config_uuid = self.state.device["config_uuid"]
        self.logger.debug("state.device.config_uuid = {}".format(config_uuid))

        # Spawn the threads this object controls
        self.recipe.spawn()
        self.event.spawn()
        self.iot.spawn()
        self.resource.spawn()
        self.connect.spawn()
        self.upgrade.spawn()

        # Create peripheral managers and spawn threads
        self.create_peripherals()
        self.spawn_peripherals()

        # Create controller managers and spawn threads
        self.create_controllers()
        self.spawn_controllers()

        # Wait for all threads to initialize
        while not self.all_threads_initialized():
            time.sleep(0.2)

        # Transition to NORMAL
        self.mode = Modes.NORMAL

    def run_normal_mode(self):
        """Runs normal operation mode. Updates device state summary and stores device 
        state in database, waits for new config command then transitions to CONFIG. 
        Transitions to ERROR on error."""
        self.logger.info("Entered NORMAL")

        while True:
            # Overwrite system state in database every 100ms
            self.update_state()

            # Store environment state in every 10 minutes
            if time.time() - self.latest_environment_timestamp > 60 * 10:
                self.store_environment()

            # Once a minute, publish any changed values
            if time.time() - self.latest_publish_timestamp > 60:
                self.latest_publish_timestamp = time.time()
                self.iot.publish()

            # Check for events
            request = self.request
            if self.request != None:
                self.request = None
                self.process_event(request)

            # Check for system error
            if self.mode == Modes.ERROR:
                self.logger.error("System received ERROR")
                break

            # Check for new configuration
            if self.mode == Modes.CONFIG:
                self.logger.info("Transitioning to CONFIG")
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_load_mode(self):
        """ Runs load mode. Stops peripheral and controller threads, loads 
            config into stored state, transitions to CONFIG. """
        self.logger.info("Entered LOAD")

        # Stop peripheral and controller threads
        self.stop_peripheral_threads()
        self.stop_controller_threads()

        # Load config into stored state

        # Transition to CONFIG
        self.mode = Modes.CONFIG

    def run_reset_mode(self):
        """ Runs reset mode. Kills peripheral and controller threads, clears 
            error state, then transitions to INIT. """
        self.logger.info("Entered RESET")

        # Kills peripheral and controller threads
        self.kill_peripheral_threads()
        self.kill_controller_threads()
        self.recipe.stop()
        self.event.stop()
        self.iot.stop()

        # Transition to INIT
        self.mode = Modes.INIT

    def run_error_mode(self):
        """ Runs error mode. Shuts down peripheral and controller threads, 
            waits for reset signal then transitions to RESET. """
        self.logger.info("Entered ERROR")

        # Shuts down peripheral and controller threads
        self.shutdown_peripheral_threads()
        self.shutdown_controller_threads()

        # Loop forever
        while True:

            # Check for reset
            if self.mode == Modes.RESET:
                break

            # Update every 100ms
            time.sleep(0.1)

    def update_state(self):
        """Updates stored state in database. If state does not exist, creates it."""

        # TODO: Move this to state manager

        if not StateModel.objects.filter(pk=1).exists():
            StateModel.objects.create(
                id=1,
                device=json.dumps(self.state.device),
                recipe=json.dumps(self.state.recipe),
                environment=json.dumps(self.state.environment),
                peripherals=json.dumps(self.state.peripherals),
                controllers=json.dumps(self.state.controllers),
                iot=json.dumps(self.state.iot),
                resource=json.dumps(self.state.resource),
                connect=json.dumps(self.state.connect),
                upgrade=json.dumps(self.state.upgrade),
            )
        else:
            StateModel.objects.filter(pk=1).update(
                device=json.dumps(self.state.device),
                recipe=json.dumps(self.state.recipe),
                environment=json.dumps(self.state.environment),
                peripherals=json.dumps(self.state.peripherals),
                controllers=json.dumps(self.state.controllers),
                iot=json.dumps(self.state.iot),
                resource=json.dumps(self.state.resource),
                connect=json.dumps(self.state.connect),
                upgrade=json.dumps(self.state.upgrade),
            )

    def load_local_data_files(self):
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

        # Load peripherals after sensor/actuator variable since verification
        # depends on them
        self.load_peripheral_setup_files()

        # Load device config after peripheral setups since verification
        # depends on  them
        self.load_device_config_files()

    def load_sensor_variables_file(self):
        """ Loads sensor variables file into database after removing all 
            existing entries. """
        self.logger.debug("Loading sensor variables file")

        # Load sensor variables and schema
        sensor_variables = json.load(open("data/variables/sensor_variables.json"))
        sensor_variables_schema = json.load(open("data/schemas/sensor_variables.json"))

        # Validate sensor variables with schema
        validate(sensor_variables, sensor_variables_schema)

        # Delete sensor variables tables
        SensorVariableModel.objects.all().delete()

        # Create sensor variables table
        for sensor_variable in sensor_variables:
            SensorVariableModel.objects.create(json=json.dumps(sensor_variable))

    def load_actuator_variables_file(self):
        """ Loads actuator variables file into database after removing all 
            existing entries. """
        self.logger.debug("Loading actuator variables file")

        # Load actuator variables and schema
        actuator_variables = json.load(open("data/variables/actuator_variables.json"))
        actuator_variables_schema = json.load(
            open("data/schemas/actuator_variables.json")
        )

        # Validate actuator variables with schema
        validate(actuator_variables, actuator_variables_schema)

        # Delete actuator variables tables
        ActuatorVariableModel.objects.all().delete()

        # Create actuator variables table
        for actuator_variable in actuator_variables:
            ActuatorVariableModel.objects.create(json=json.dumps(actuator_variable))

    def load_cultivars_file(self):
        """ Loads cultivars file into database after removing all 
            existing entries."""
        self.logger.debug("Loading cultivars file")

        # Load cultivars and schema
        cultivars = json.load(open("data/cultivations/cultivars.json"))
        cultivars_schema = json.load(open("data/schemas/cultivars.json"))

        # Validate cultivars with schema
        validate(cultivars, cultivars_schema)

        # Delete cultivars tables
        CultivarModel.objects.all().delete()

        # Create cultivars table
        for cultivar in cultivars:
            CultivarModel.objects.create(json=json.dumps(cultivar))

    def load_cultivation_methods_file(self):
        """ Loads cultivation methods file into database after removing all 
            existing entries. """
        self.logger.debug("Loading cultivation methods file")

        # Load cultivation methods and schema
        cultivation_methods = json.load(
            open("data/cultivations/cultivation_methods.json")
        )
        cultivation_methods_schema = json.load(
            open("data/schemas/cultivation_methods.json")
        )

        # Validate cultivation methods with schema
        validate(cultivation_methods, cultivation_methods_schema)

        # Delete cultivation methods tables
        CultivationMethodModel.objects.all().delete()

        # Create cultivation methods table
        for cultivation_method in cultivation_methods:
            CultivationMethodModel.objects.create(json=json.dumps(cultivation_method))

    def load_recipe_files(self):
        """Loads recipe files into database via recipe manager create or update function."""
        self.logger.debug("Loading recipe files")

        # Get recipes
        for filepath in glob.glob("data/recipes/*.json"):
            self.logger.debug("Loading recipe file: {}".format(filepath))
            with open(filepath, "r") as f:
                json_ = f.read().replace("\n", "")
                message, code = self.recipe.create_or_update_recipe(json_)
                if code != 200:
                    filename = filepath.split("/")[-1]
                    error = "Unable to load {} ({})".format(filename, message)
                    self.logger.error(error)

    def load_peripheral_setup_files(self):
        """ Loads peripheral setup files from codebase into database by 
            creating new entries after deleting existing entries. Verification 
            depends on sensor/actuator variables. """
        self.logger.info("Loading peripheral setup files")

        # Get peripheral setups
        peripheral_setups = []
        for filepath in glob.glob("device/peripherals/modules/*/setups/*.json"):
            self.logger.debug("Loading peripheral setup file: {}".format(filepath))
            peripheral_setups.append(json.load(open(filepath)))

        # Get get peripheral setup schema
        # TODO: Finish schema
        peripheral_setup_schema = json.load(open("data/schemas/peripheral_setup.json"))

        # Validate peripheral setups with schema
        for peripheral_setup in peripheral_setups:
            validate(peripheral_setup, peripheral_setup_schema)

        # Delete all peripheral setup entries from database
        PeripheralSetupModel.objects.all().delete()

        # TODO: Validate peripheral setup variables with database variables

        # Create peripheral setup entries in database
        for peripheral_setup in peripheral_setups:
            PeripheralSetupModel.objects.create(json=json.dumps(peripheral_setup))

    def load_device_config_files(self):
        """ Loads device config files from codebase into database by creating 
            new entries after deleting existing entries. Verification depends 
            on peripheral setups. """
        self.logger.info("Loading device config files")

        # Get devices
        device_configs = []
        for filepath in glob.glob("data/devices/*.json"):
            self.logger.debug("Loading device config file: {}".format(filepath))
            device_configs.append(json.load(open(filepath)))

        # Get get device config schema
        # TODO: Finish schema (see optional objects)
        device_config_schema = json.load(open("data/schemas/device_config.json"))

        # Validate device configs with schema
        for device_config in device_configs:
            validate(device_config, device_config_schema)

        # TODO: Validate device config with peripherals
        # TODO: Validate device config with varibles

        # Delete all device config entries from database
        DeviceConfigModel.objects.all().delete()

        # Create device config entry if new or update existing
        for device_config in device_configs:
            DeviceConfigModel.objects.create(json=json.dumps(device_config))

    def load_database_stored_state(self):
        """ Loads stored state from database if it exists. """
        self.logger.info("Loading database stored state")

        # Get stored state from database
        if not StateModel.objects.filter(pk=1).exists():
            self.logger.info("No stored state in database")
            self.config_uuid = None
            return
        stored_state = StateModel.objects.filter(pk=1).first()

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

    def store_environment(self):
        """ Stores current environment state in environment table. """
        EnvironmentModel.objects.create(state=self.state.environment)

    def create_peripherals(self):
        """ Creates peripheral managers. """
        self.logger.info("Creating peripheral managers")

        # Verify peripherals are configured
        if self.config_dict["peripherals"] == None:
            self.logger.info("No peripherals configured")
            return

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
        for peripheral_config_dict in self.config_dict["peripherals"]:
            self.logger.debug("Creating {}".format(peripheral_config_dict["name"]))

            # Get peripheral setup dict
            peripheral_uuid = peripheral_config_dict["uuid"]
            peripheral_setup_dict = self.get_peripheral_setup_dict(peripheral_uuid)

            # Verify valid peripheral config dict
            if peripheral_setup_dict == None:
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

    def get_peripheral_setup_dict(self, uuid):
        """ Gets peripheral setup dict for uuid in peripheral setup table. """
        if not PeripheralSetupModel.objects.filter(uuid=uuid).exists():
            return None
        return json.loads(PeripheralSetupModel.objects.get(uuid=uuid).json)

    def spawn_peripherals(self):
        """ Spawns peripheral threads. """
        if self.peripherals == None:
            self.logger.info("No peripheral threads to spawn")
        else:
            self.logger.info("Spawning peripheral threads")
            for peripheral_name in self.peripherals:
                self.peripherals[peripheral_name].spawn()

    def create_controllers(self):
        """ Creates controller managers. """
        self.logger.info("Creating controller managers")

        # Verify controllers are configured
        if self.config_dict["controllers"] == None:
            self.logger.info("No controllers configured")
            return

        # Create controller managers
        self.controllers = {}
        for controller_config_dict in self.config_dict["controllers"]:
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
                "device.controllers.drivers." + controller_setup_dict["module_name"]
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

    def spawn_controllers(self):
        """ Spawns controller threads. """
        if self.controllers == None:
            self.logger.info("No controller threads to spawn")
        else:
            self.logger.info("Spawning controller threads")
            for controller_name in self.controllers:
                self.controllers[controller_name].spawn()

    def all_threads_initialized(self):
        """ Checks that all recipe, peripheral, and controller 
            theads are initialized. """
        if self.state.recipe["mode"] == Modes.INIT:
            return False
        elif not self.all_peripherals_initialized():
            return False
        elif not self.all_controllers_initialized():
            return False
        return True

    def all_peripherals_initialized(self):
        """ Checks that all peripheral threads have transitioned from INIT. """
        for peripheral_name in self.state.peripherals:
            peripheral_state = self.state.peripherals[peripheral_name]

            # Check if mode in peripheral state
            if "mode" not in peripheral_state:
                return False

            # Check if mode either init or setup
            if peripheral_state["mode"] == Modes.INIT:
                return False
        return True

    def all_controllers_initialized(self):
        """ Checks that all controller threads have transitioned from INIT. """
        for controller_name in self.state.controllers:
            controller_state = self.state.controllers[controller_name]
            if controller_state["mode"] == Modes.INIT:
                return False
        return True

    def kill_peripheral_threads(self):
        """ Kills all peripheral threads. """

    # TODO this needs work
    # for peripheral_name in self.state.peripherals:
    #    self.state.peripherals[peripheral_name].thread_is_active = False

    def kill_controller_threads(self):
        """ Kills all controller threads. """

    # TODO this needs work
    # for controller_name in self.state.controller:
    #    self.state.controller[controller_name].thread_is_active = False

    def shutdown_peripheral_threads(self):
        """ Shuts down peripheral threads. """
        ...

        # TODO: Fix this

        # for peripheral_name in self.peripherals:
        #     self.periphrals[peripheral_name].commanded_mode = Modes.SHUTDOWN

    def shutdown_controller_threads(self):
        """ Shuts down controller threads. """
        ...

        # TODO: Fix this

        # for controller_name in self.controllers:
        #     self.controllers[controller_name].commanded_mode = Modes.SHUTDOWN
