# Import standard python modules
import threading
from typing import Optional, Tuple, Dict

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.logger import Logger
from device.utilities.error import Error

# Import peripheral utilities
from device.peripherals.utilities import light

# Import peripheral parent class
from device.peripherals.classes.peripheral_manager import PeripheralManager

# Import led array and events
from device.peripherals.modules.led_dac5578.array import LEDDAC5578Array
from device.peripherals.modules.led_dac5578.events import LEDDAC5578Events


class LEDDAC5578Manager(PeripheralManager, LEDDAC5578Events):
    """ Manages an LED array controlled by a dac5578. """

    _prev_desired_ppfd = None
    _prev_desired_spectrum = None
    _prev_desired_distance = None

    def __init__(self, *args, **kwargs):
        """ Instantiates light array. Instantiates parent class, and initializes 
            sensor variable name. """

        # Instantiate parent class
        super().__init__(*args, **kwargs)

        # Initialize panel and channel configs
        self.panel_configs = self.parameters["communication"]["panels"]
        self.channel_configs = self.setup_dict["channel_configs"]

        # Initialize variable names
        self.ppfd_name = self.parameters["variables"]["sensor"]["ppfd_umol_m2_s"]
        self.spectrum_name = self.parameters["variables"]["sensor"][
            "spectrum_nm_percent"
        ]
        self.distance_name = self.parameters["variables"]["sensor"][
            "illumination_distance_cm"
        ]
        self.channel_outputs_name = self.parameters["variables"]["actuator"][
            "channel_output_percents"
        ]

        # Instantiate LED array
        self.array = LEDDAC5578Array(
            name=self.name,
            panel_configs=self.panel_configs,
            channel_configs=self.channel_configs,
            simulate=self.simulate,
        )

    @property
    def spectrum(self) -> None:
        """ Gets spectrum value. """
        return self.state.get_peripheral_reported_sensor_value(
            self.name, self.spectrum_name
        )

    @spectrum.setter
    def spectrum(self, value: dict) -> None:
        """ Sets spectrum value in shared state. """
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.spectrum_name, value
        )
        self.state.set_environment_reported_sensor_value(
            self.name, self.spectrum_name, value, simple=True
        )

    @property
    def desired_spectrum(self) -> dict:
        """ Gets desired spectrum value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """
        if self.mode != Modes.MANUAL:
            return self.state.get_environment_desired_sensor_value(self.spectrum_name)
        else:
            return self.state.get_peripheral_desired_sensor_value(
                self.name, self.spectrum_name
            )

    @property
    def ppfd(self) -> float:
        """ Gets ppfd value. """
        return self.state.get_peripheral_reported_sensor_value(
            self.name, self.ppfd_name
        )

    @ppfd.setter
    def ppfd(self, value: float) -> None:
        """ Sets ppfd value in shared state. """
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.ppfd_name, value
        )
        self.state.set_environment_reported_sensor_value(
            self.name, self.ppfd_name, value, simple=True
        )

    @property
    def desired_ppfd(self) -> float:
        """ Gets desired ppfd value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """
        if self.mode != Modes.MANUAL:
            return self.state.get_environment_desired_sensor_value(self.ppfd_name)
        else:
            return self.state.get_peripheral_desired_sensor_value(
                self.name, self.ppfd_name
            )

    @property
    def distance(self) -> float:
        """ Gets distance value. """
        return self.state.get_peripheral_reported_sensor_value(
            self.name, self.distance_name
        )

    @distance.setter
    def distance(self, value: float) -> None:
        """ Sets distance value in shared state. """
        self.state.set_peripheral_reported_sensor_value(
            self.name, self.distance_name, value
        )
        self.state.set_environment_reported_sensor_value(
            self.name, self.distance_name, value, simple=True
        )

    @property
    def desired_distance(self) -> float:
        """ Gets desired distance value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """
        if self.mode != Modes.MANUAL:
            return self.state.get_environment_desired_sensor_value(self.distance_name)
        else:
            return self.state.get_peripheral_desired_sensor_value(
                self.name, self.distance_name
            )

    @property
    def channel_outputs(self) -> dict:
        """ Gets distance value. """
        return self.state.get_peripheral_reported_actuator_value(
            self.name, self.channel_outputs_name
        )

    @channel_outputs.setter
    def channel_outputs(self, value: dict) -> None:
        """ Sets channel outputs value in shared state. """
        self.state.set_peripheral_reported_actuator_value(
            self.name, self.channel_outputs_name, value
        )
        self.state.set_environment_reported_actuator_value(
            self.channel_outputs_name, value
        )

    @property
    def desired_channel_outputs(self) -> dict:
        """ Gets desired distance value from shared environment state if not 
            in manual mode, otherwise gets it from peripheral state. """
        if self.mode != Modes.MANUAL:
            return self.state.get_environment_desired_actuator_value(
                self.channel_outputs_name
            )
        else:
            return self.state.get_peripheral_desired_actuator_value(
                self.name, self.channel_outputs_name
            )

    def initialize(self) -> None:
        """ Initializes led manager. """
        self.logger.debug("Initializing")

        # Set initial parameters
        self.clear_reported_values()

        # Initialize array
        error = self.array.initialize()

        # Check for errors
        if error.exists():
            error.report("Unable to initialize manager")
            self.logger.error(error.summary())
            self.mode = Modes.ERROR
            return

        # Successful initialization!
        self.logger.debug("Initialized successfully")

    def setup(self) -> None:
        """ Sets up led manager. """
        self.logger.debug("Setting up")

        # Turn off all panels in array
        error = self.array.turn_off()

        # Check for errors
        if error.exists():
            error.report("Unable to setup")
            self.logger.error(error.summary())
            self.mode = Modes.ERROR
            return

        # Update reported variables
        self.update_reported_variables()

        # Successful setup!
        self.logger.debug("Setup successfully")

    def update(self) -> None:
        """ Updates led array if desired spectrum, ppfd, or distance value 
            changes. """

        # Initialize update flag
        update = False

        # Check for new desired ppfd
        if self.desired_ppfd != None and self.desired_ppfd != self._prev_desired_ppfd:
            self.logger.info("Received new desired ppfd")
            self.logger.debug("desired_ppfd = {} Watts".format(self.desired_ppfd))
            self.distance = self.desired_distance
            update = True

        # Check for new desired spectrum
        if (
            self.desired_spectrum != None
            and self.desired_spectrum != self._prev_desired_spectrum
        ):
            self.logger.info("Received new desired spectrum")
            self.logger.debug("desired_spectrum = {}".format(self.desired_spectrum))
            update = True

        # Check for new illumination distance
        if (
            self.desired_distance != None
            and self.desired_distance != self._prev_desired_distance
        ):
            self.logger.info("Received new desired illumination distance")
            self.logger.debug("desired_distance = {} cm".format(self.desired_distance))
            update = True

        # Check if update is required
        if not update:
            return

        # Verify all desired values exist:
        if (
            self.desired_ppfd == None
            or self.desired_spectrum == None
            or self.desired_distance == None
        ):
            self.logger.warning("Unable to update, not all desired values are set")
            return

        # Set spectral power distribution from desired values
        result = self.array.set_spd(
            desired_distance_cm=self.desired_distance,
            desired_ppfd_umol_m2_s=self.desired_ppfd,
            desired_spectrum_nm_percent=self.desired_spectrum,
        )

        # Check for errors
        error = result[3]
        if error.exists():
            error.report("Unable to set spd")
            self.logger.error(error.summary())
            self.mode = Modes.ERROR
            return

        # Update reported values
        self.channel_outputs = result[0]
        self.spectrum = result[1]
        self.ppfd = result[2]

        # Update prev desired values
        self._prev_desired_ppfd = self.desired_ppfd
        self._prev_desired_spectrum = self.desired_spectrum
        self._prev_desired_distance = self.desired_distance

        # Successfully updated!
        self.logger.debug("Successfully updated")

    def reset(self) -> None:
        """ Resets manager. """
        self.array.reset()
        self._prev_desired_ppfd = None
        self._prev_desired_spectrum = None
        self._prev_desired_distance = None

    def shutdown(self) -> None:
        """ Shuts down manager. """
        self.array.shutdown()

    def clear_reported_values(self):
        """ Clears reported values. """
        self.health = None
        self.ppfd = None
        self.spectrum = None
        self.distance = None
        self.channel_outputs = None

    def update_reported_variables(self):
        """ Updates reported variables. """

        # Get channel outputs stored in array
        self.channel_outputs = self.array.channel_outputs

        # Get previously used distance or default setup distance
        if self.distance == None:
            self.distance = self.channel_configs[0]["planar_distance_map"][0][
                "distance_cm"
            ]

        # Get previously used spectrum or default setup spectrum for reference spd
        if self.spectrum != None:
            reference_spd = self.spectrum
        else:
            reference_spd = self.channel_configs[0]["spectrum_nm_percent"]

        # Calculate resultant spectrum and ppfd
        self.spectrum, self.ppfd = light.calculate_resultant_spd(
            channel_configs=self.channel_configs,
            reference_spd=reference_spd,
            channel_output_setpoints=self.channel_outputs,
            distance=self.distance,
        )

        # Update health
        self.health = self.array.health
