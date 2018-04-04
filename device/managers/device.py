# Import python modules
import logging, time, json, threading, os, sys, glob

# Import django modules
from django.db.models.signals import post_save
from django.dispatch import receiver

# Import device utilities
from device.utilities.mode import Mode
from device.utilities.error import Error
from device.utilities.variable import Variable

# Import device validators
from device.utilities.validators import PeripheralSetupValidator
from device.utilities.validators import DeviceConfigValidator
from device.utilities.validators import RecipeValidator

# Import shared memory
from device.state import State

# Import device managers
from device.managers.recipe import RecipeManager
from device.managers.event import EventManager

# Import database models
from app.models import StateModel
from app.models import EventModel
from app.models import EnvironmentModel
from app.models import PeripheralSetupModel
from app.models import DeviceConfigModel



class DeviceManager:
    """ A state machine that spawns threads to run recipes, read sensors, set 
    actuators, manage control loops, sync data, and manage external events. """

    # Initialize logger
    extra = {"console_name":"Device", "file_name": "device"}
    logger = logging.getLogger(__name__)
    logger = logging.LoggerAdapter(logger, extra)

    # Initialize device mode and error
    _mode = None
    _error = None

    # Initialize state object, `state` serves as shared memory between threads
    # Note: Thread should be locked whenever writing to `state` object to 
    # avoid memory corruption.
    state = State()

    # Initialize environment state dict
    state.environment = {
        "sensor": {"desired": {}, "reported": {}},
        "actuator": {"desired": {}, "reported": {}},
        "reported_sensor_stats": {
        "individual": {
                "instantaneous": {},
                "average": {}
            },
            "group": {
                "instantaneous": {},
                "average": {}
            }
        }
    }

    # Initialize recipe state dict
    state.recipe = {
        "recipe_uuid": None,
        "start_timestamp_minutes": None,
        "last_update_minute": None
    }

    # Initialize recipe object
    recipe = RecipeManager(state)

    # Intialize event object
    event = EventManager(state)
    post_save.connect(event.process, sender=EventModel)


    # Initialize peripheral and controller managers
    peripheral_managers = None
    controller_managers = None


    def __init__(self):
        """ Initializes device. """
        self.mode = Mode.INIT
        self.error = Error.NONE


    @property
    def mode(self):
        """ Gets mode. """
        return self._mode


    @mode.setter
    def mode(self, value):
        """ Safely updates mode in state object. """
        self._mode = value
        with threading.Lock():
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
        with threading.Lock():
            self.state.device["commanded_mode"] = value


    @property
    def error(self):
        """ Gets device error. """
        return self._error


    @error.setter
    def error(self, value):
        """ Safely updates error in shared state. """
        self._error = value
        with threading.Lock():
            self.state.device["error"] = value


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
        with threading.Lock():
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
        """ Safely updates commanded config uuid in state. """
        with threading.Lock():
            self.state.device["commanded_config_uuid"] = value


    @property
    def config_dict(self):
        """ Gets config dict for config uuid in device config table. """
        if self.config_uuid == None:
            return None
        config = DeviceConfigModel.objects.get(uuid=self.config_uuid)
        return json.loads(config.json)


    @property
    def latest_environment_timestamp(self):
        """ Gets latest environment timestamp from environment table. """
        if not EnvironmentModel.objects.all():
            return 0
        else:
            environment = EnvironmentModel.objects.latest()
            return environment.timestamp.timestamp()


    def spawn(self, delay=None):
        """ Spawns device thread. """
        self.thread = threading.Thread(target=self.run_state_machine, args=(delay,))
        self.thread.daemon = True
        self.thread.start()


    def run_state_machine(self, delay=None):
        """ Runs device state machine. """
        
        # Wait for optional delay
        if delay != None:
            time.sleep(delay)

        self.logger.info("Spawing device thread")

        # Start state machine
        self.logger.info("Started state machine")
        while True:
            if self.mode == Mode.INIT:
                self.run_init_mode()
            elif self.mode == Mode.CONFIG:
                self.run_config_mode()
            elif self.mode == Mode.SETUP:
                self.run_setup_mode()
            elif self.mode == Mode.NORMAL:
                self.run_normal_mode()
            elif self.mode == Mode.LOAD:
                self.run_load_mode()
            elif self.mode == Mode.ERROR:
                self.run_error_mode()
            elif self.mode == Mode.RESET:
                self.run_reset_mode()


    def run_init_mode(self):
        """ Runs initialization mode. Loads stored state from database then 
            transitions to CONFIG. """
        self.logger.info("Entered INIT")

        # Introspet and load peripheral setups into database
        setup_dicts = self.introspect_peripheral_setups()
        self.store_peripheral_setups(setup_dicts)

        # Introspect and load device configs into database
        config_dicts = self.introspect_device_configs()
        self.store_device_configs(config_dicts)

        # Load stored state from database
        self.load_state()

        # Transition to CONFIG
        self.mode = Mode.CONFIG


    def run_config_mode(self):
        """ Runs configuration mode. If device config is not set, waits for 
            config command then transitions to SETUP. """
        self.logger.info("Entered CONFIG")

        # If device config is not set, wait for config command
        if self.config_uuid == None:
            self.logger.info("Waiting for config command")

            # Fake config command during development
            self.commanded_config_uuid = "64d72849-2e30-4a4c-8d8c-71b6b3384126"

            while True:
                if self.commanded_config_uuid != None:
                    self.config_uuid = self.commanded_config_uuid
                    self.commanded_config_uuid = None
                    break
                # Update every 100ms
                time.sleep(0.1)

        # Transition to SETUP
        self.mode = Mode.SETUP


    def run_setup_mode(self):
        """ Runs setup mode. Creates and spawns recipe, peripheral, and 
            controller threads, waits for all threads to initialize then 
            transitions to NORMAL. """
        self.logger.info("Entered SETUP")

        # Spawn recipe
        self.recipe.spawn()

        # Create peripheral managers and spawn threads
        self.create_peripheral_managers()
        self.spawn_peripheral_threads()

        # Create controller managers and spawn threads
        self.create_controller_managers()
        self.spawn_controller_threads()

        # Wait for all threads to initialize
        while not self.all_threads_initialized():
            time.sleep(0.2)

        # Transition to NORMAL
        self.mode = Mode.NORMAL


    def run_normal_mode(self):
        """ Runs normal operation mode. Updates device state summary and 
            stores device state in database, waits for new config command then
            transitions to CONFIG. Transitions to ERROR on error."""
        self.logger.info("Entered NORMAL")

        while True:
            # Overwrite system state in database every 100ms
            self.update_state()

            # Store environment state in every 10 minutes 
            if time.time() - self.latest_environment_timestamp > 60*10:
                self.store_environment()
            
            # Check for system error
            if self.mode == Mode.ERROR:
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
        self.error = Error.NONE

        # Transition to CONFIG
        self.mode = Mode.CONFIG

 
    def run_reset_mode(self):
        """ Runs reset mode. Kills peripheral and controller threads, clears 
            error state, then transitions to INIT. """
        self.logger.info("Entered RESET")

        # Kills peripheral and controller threads
        self.kill_peripheral_threads()
        self.kill_controller_threads()

        # Clear errors
        self.error = Error.NONE

        # Transition to INIT
        self.mode = Mode.INIT


    def run_error_mode(self):
        """ Runs error mode. Shuts down peripheral and controller threads, 
            waits for reset signal then transitions to RESET. """
        self.logger.info("Entered ERROR")

        # Shuts down peripheral and controller threads
        self.shutdown_peripheral_threads()
        self.shutdown_controller_threads()

        # Wait for reset
        while True:
            if self.mode == Mode.RESET:
                break

            # Update every 100ms
            time.sleep(0.1) # 100ms


    def update_state(self):
        """ Updates stored state in database. If state does not exist, 
            creates it. """

        if not StateModel.objects.filter(pk=1).exists():
            StateModel.objects.create(
                id=1,
                device = json.dumps(self.state.device),
                recipe = json.dumps(self.state.recipe),
                environment = json.dumps(self.state.environment),
                peripherals = json.dumps(self.state.peripherals),
                controllers = json.dumps(self.state.controllers),
            )
        else:
            StateModel.objects.filter(pk=1).update(
                device = json.dumps(self.state.device),
                recipe = json.dumps(self.state.recipe),
                environment = json.dumps(self.state.environment),
                peripherals = json.dumps(self.state.peripherals),
                controllers = json.dumps(self.state.controllers),
            )


    def load_state(self):
        """ Loads stored state from database if it exists. """
        self.logger.info("Loading state")

        # Get stored state from database
        if not StateModel.objects.filter(pk=1).exists():
            self.logger.debug("No stored state in database")
            self.config_uuid = None
            return
        stored_state = StateModel.objects.filter(pk=1).first()

        # Load device state
        stored_device_state = json.loads(stored_state.device)
        self.config_uuid = stored_device_state["config_uuid"]

        # Load recipe state
        stored_recipe_state = json.loads(stored_state.recipe)
        self.recipe.recipe_uuid = stored_recipe_state["recipe_uuid"]
        self.recipe.recipe_name = stored_recipe_state["recipe_name"]
        self.recipe.duration_minutes = stored_recipe_state["duration_minutes"]
        self.recipe.start_timestamp_minutes = stored_recipe_state["start_timestamp_minutes"]
        self.recipe.last_update_minute = stored_recipe_state["last_update_minute"]
        self.recipe.stored_mode = stored_recipe_state["mode"]

        # Load peripherals state
        stored_peripherals_state = json.loads(stored_state.peripherals)
        for peripheral_name in stored_peripherals_state:
            if "stored" in stored_peripherals_state[peripheral_name]:
                self.state.peripherals[peripheral_name] = {}
                self.state.peripherals[peripheral_name]["stored"] = stored_peripherals_state[peripheral_name]["stored"]

        # Load controllers state
        stored_controllers_state = json.loads(stored_state.controllers)
        for controller_name in stored_controllers_state:
            if "stored" in stored_controllers_state[controller_name]:
                self.state.controllers[controller_name] = {}
                self.state.controllers[controller_name]["stored"] = stored_controllers_state[controller_name]["stored"]


   
    def store_environment(self):
        """ Stores current environment state in environment table. """
        EnvironmentModel.objects.create(state=self.state.environment)


    def introspect_peripheral_setups(self):
        """ Looks through peripheral setup files in codebase to generate 
        peripheral setup dicts. """
        self.logger.info("Introspecting peripheral setups")

        # Load peripheral setup filepaths
        setup_filepaths = []
        base_dir = "device/peripherals/setups/"
        for filepath in glob.glob(base_dir + "*.json"):
            setup_filepaths.append(filepath)

        # Verify peripheral setup files and build config dicts
        setup_dicts = []
        peripheral_setup_validator = PeripheralSetupValidator()
        for setup_filepath in setup_filepaths:
            error_message = peripheral_setup_validator.validate(setup_filepath, filepath=True)
            if error_message != None:
                raise Exception(error_message)
            else:
                setup_dicts.append(json.load(open(setup_filepath)))

        # Return peripheral setup dicts
        return setup_dicts


    def store_peripheral_setups(self, setup_dicts):
        """ Stores peripheral setup dicts in database after deleting 
            existing entries. """

        # Delete all peripheral setup entries
        PeripheralSetupModel.objects.all().delete()

        # Create peripheral setup entries
        for setup_dict in setup_dicts:
            PeripheralSetupModel.objects.create(json=json.dumps(setup_dict))


    def introspect_device_configs(self):
        """ Looks through device config files in codebase to generate 
        device config dicts. """
        self.logger.info("Introspecting device configs")

        # Load device config filepaths
        config_filepaths = []
        base_dir = "device/configs/"
        for filepath in glob.glob(base_dir + "*.json"):
            config_filepaths.append(filepath)

        # Verify device config files and build config dicts
        config_dicts = []
        device_config_validator = DeviceConfigValidator()
        for config_filepath in config_filepaths:

            error_message = device_config_validator.validate(config_filepath, filepath=True)
            if error_message != None:
                raise Exception(error_message)
            else:
                config_dicts.append(json.load(open(config_filepath)))

        # Return device config dicts
        return config_dicts  


    def store_device_configs(self, config_dicts):
        """ Stores device config dicts in database by creating entry if new or
            updating existing. """

        # Create device config entry if new or update existing
        for config_dict in config_dicts:
            uuid = config_dict["uuid"]
            if DeviceConfigModel.objects.filter(uuid=uuid).exists():
                DeviceConfigModel.objects.update(uuid=uuid, json=json.dumps(config_dict))
            else:
                DeviceConfigModel.objects.create(json=json.dumps(config_dict))


    def create_peripheral_managers(self):
        """ Creates peripheral managers. """
        self.logger.info("Creating peripheral managers")

        # Verify peripherals are configured
        if self.config_dict["peripherals"] == None:
            self.logger.info("No peripherals configured")
            return

        # Create peripheral managers
        self.peripheral_managers = {}
        for peripheral_config_dict in self.config_dict["peripherals"]:
            self.logger.debug("Creating {}".format(peripheral_config_dict["name"]))
            
            # Get peripheral setup dict
            peripheral_uuid = peripheral_config_dict["uuid"]
            peripheral_setup_dict = self.get_peripheral_setup_dict(peripheral_uuid)

            # Verify valid peripheral config dict
            if peripheral_setup_dict == None:
                self.logger.critical("Invalid peripheral uuid in device "
                    "config. Validator should have caught this.")
                continue

            # Get peripheral module and class name
            module_name = "device.peripherals.drivers." + peripheral_setup_dict["module_name"]
            class_name = peripheral_setup_dict["class_name"]

            # Import peripheral library
            module_instance= __import__(module_name, fromlist=[class_name])
            class_instance = getattr(module_instance, class_name)

            # Create peripheral manager
            peripheral_name = peripheral_config_dict["name"]
            peripheral_manager = class_instance(peripheral_name, self.state, peripheral_config_dict)
            self.peripheral_managers[peripheral_name] = peripheral_manager


    def get_peripheral_setup_dict(self, uuid):
        """ Gets peripheral setup dict for uuid in peripheral setup table. """
        if not PeripheralSetupModel.objects.filter(uuid=uuid).exists():
            return None
        return json.loads(PeripheralSetupModel.objects.get(uuid=uuid).json)


    def spawn_peripheral_threads(self):
        """ Spawns peripheral threads. """
        if self.peripheral_managers == None:
            self.logger.info("No peripheral threads to spawn")
        else:
            self.logger.info("Spawning peripheral threads")
            for peripheral_name in self.peripheral_managers:
                self.peripheral_managers[peripheral_name].spawn()


    def create_controller_managers(self):
        """ Creates controller managers. """
        self.logger.info("Creating controller managers")

        # Verify controllers are configured
        if self.config_dict["controllers"] == None:
            self.logger.info("No controllers configured")
            return

        # Create controller managers
        self.controller_managers = {}
        for controller_config_dict in self.config_dict["controllers"]:
            self.logger.debug("Creating {}".format(controller_config_dict["name"]))
            
            # Get controller setup dict
            controller_uuid = controller_config_dict["uuid"]
            controller_setup_dict = self.get_controller_setup_dict(controller_uuid)

            # Verify valid controller config dict
            if controller_setup_dict == None:
                self.logger.critical("Invalid controller uuid in device "
                    "config. Validator should have caught this.")
                continue

            # Get controller module and class name
            module_name = "device.controllers.drivers." + controller_setup_dict["module_name"]
            class_name = controller_setup_dict["class_name"]

            # Import controller library
            module_instance= __import__(module_name, fromlist=[class_name])
            class_instance = getattr(module_instance, class_name)

            # Create controller manager
            controller_name = controller_config_dict["name"]
            controller_manager = class_instance(controller_name, self.state, controller_config_dict)
            self.controller_managers[controller_name] = controller_manager


    def spawn_controller_threads(self):
        """ Spawns controller threads. """
        if self.controller_managers == None:
            self.logger.info("No controller threads to spawn")
        else:
            self.logger.info("Spawning controller threads")
            for controller_name in self.controller_managers:
                self.controller_managers[controller_name].spawn()


    def all_threads_initialized(self):
        """ Checks that all recipe, peripheral, and controller 
            theads are initialized. """
        if self.state.recipe["mode"] == Mode.INIT:
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
            if peripheral_state["mode"] == Mode.INIT or peripheral_state["mode"] == Mode.WARMING:
                return False
        return True


    def all_controllers_initialized(self):
        """ Checks that all controller threads have transitioned from INIT. """
        for controller_name in self.state.controllers:
            controller_state = self.state.controllers[controller_name]
            if controller_state["mode"] == Mode.INIT:
                return False
        return True


    def kill_peripheral_threads(self):
        """ Kills all peripheral threads. """
        for peripheral_name in self.peripherals:
            self.peripherals[peripheral_name].thread_is_active = False


    def kill_controller_threads(self):
        """ Kills all controller threads. """
        for controller_name in self.controller:
            self.controller[controller_name].thread_is_active = False


    def shutdown_peripheral_threads(self):
        """ Shuts down peripheral threads. """
        for peripheral_name in self.peripherals:
            self.periphrals[peripheral_name].commanded_mode = Mode.SHUTDOWN


    def shutdown_controller_threads(self):
        """ Shuts down controller threads. """
        for controller_name in self.controllers:
            self.controllers[controller_name].commanded_mode = Mode.SHUTDOWN