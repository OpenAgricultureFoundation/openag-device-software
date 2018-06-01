# Import standard python modules
from typing import Tuple, Optional 
import time

# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
from device.utilities.health import Health

# Import peripheral utilities
from device.peripherals.utilities import light

# Import device drivers
from device.peripherals.modeules.atlas_ec.driver import AtlasECDriver


class AtlasECSensor:
    """ Atlas EC sensor instance. """


    def __init__(self, name, channel_configs, bus, address, mux=None, channel=None, simulate=False):
        """ Instantiates panel. """

        # Initialize logger
        self.logger = Logger(
            name = "AtlasECSensor({})".format(name),
            dunder_name = __name__,
        )
        
        # Initialize name and channel configs
        self.name = name
        self.channel_configs = channel_configs

        # Initialize driver
        self.driver = AtlasECDriver(
            name = name,
            bus = bus,
            address = address,
            mux = mux,
            channel = channel,
            simulate = simulate,
        )

        # Initialize health metrics
        self.health = Health(updates = 5, minimum = 60)
        self.healthy = self.health.healthy


    def initialize(self) -> Error:
        """ Initializes sensor. """
        
        # Probe driver
        error = self.probe()

        # Check for errors:
        if error.exists():
            error.report("Sensor unable to initialize")
            return error

        # Successfully initialized!
        return Error(None)


    def setup(self) -> Error:
        """ Sets up sensor. """
        
        # Enable led
        error = self.enable_led()

        # Check for errors:
        if error.exists():
            error.report("Sensor unable to be setup")
            return error

        # Set probe type
        error = self.set_probe_type("1.0")

        # Check for errors:
        if error.exists():
            error.report("Sensor unable to be setup")
            return error

        # Check if using new firmware
        if self.driver.firmware_version < 1.95:
            # Successfuly setup older firmware!
            return Error(None)
        else:
            self.logger.warning("Using old circuit stamp, consider upgrading")

        # Enable protocol lock
        error = self.enable_protocol_lock()

        # Check for errors:
        if error.exists():
            error.report("Sensor unable to be setup")
            return error

        # Enable electrical conductivity output
        error = self.enable_electrical_conductivity_output()

        # Check for errors:
        if error.exists():
            error.report("Sensor unable to be setup")
            return error

        # Disable total dissolved solids output
        error = self.disable_total_dissolved_solids_output()

        # Check for errors:
        if error.exists():
            error.report("Sensor unable to be setup")
            return error

        # Disable salinity output
        error = self.disable_salinity_output()

        # Check for errors:
        if error.exists():
            error.report("Sensor unable to be setup")
            return error

        # Disable specific gravity output
        error = self.disable_specific_gravity_output()

        # Check for errors:
        if error.exists():
            error.report("Sensor unable to be setup")
            return error

        # Setup successful!
        return Error(None)


    def reset(self):
        self.health.reset()


    def shutdown(self):
        ...


        # Send enable sleep command to sensor hardware
        # try:
        #     self.enable_sleep_mode()
        #     self.logger.debug("Successfully shutdown sensor")
        # except:
        #     self.logger.exception("Sensor shutdown failed")
        #     self.mode = Modes.ERROR


    def probe(self):
        """ Probes driver until successful or becomes too unhealthy. """

        # Probe until successful or unhealthy
        while self.healthy:

            # Send probe
            error = self.driver.probe()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.health.healthy:
            error.report("Sensor probe failed, became too unhealthy")
            return error

        # Successfuly initialized!
        return Error(None)


    def enable_led(self) -> Error:
        """ Tries to enable protocol lock until successful or becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.enable_led()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.health.healthy:
            error.report("Sensor unable to enable led, became too unhealthy")
            return error

        # Successfuly enabled led!
        return Error(None)


    def set_probe_type(self, value: str) -> Error:
        """ Tries to enable protocol lock until successful or becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.set_probe_type(value)

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.health.healthy:
            error.report("Sensor unable to set probe type, became too unhealthy")
            return error

        # Successfuly set probe type!
        return Error(None)


    def enable_protocol_lock(self) -> Error:
        """ Tries to enable protocol lock until successful or becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.enable_protocol_lock()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.health.healthy:
            error.report("Sensor unable to enable protocol lock, became too unhealthy")
            return error

        # Successfuly enabled protocol lock!
        return Error(None)


    def enable_electrical_conductivity_output(self) -> Error:
        """ Tries to enable electrical conductivity output until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.enable_electrical_conductivity_output()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.health.healthy:
            error.report("Sensor unable to enable electrical conductivity output, became too unhealthy")
            return error

        # Successfuly enabled electrical conductivity output!
        return Error(None)


    def disable_total_dissolved_solids_output(self) -> Error:
        """ Tries to disable electrical conductivity output until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.disable_total_dissolved_solids_output()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.health.healthy:
            error.report("Sensor unable to disable total dissolved solids output, became too unhealthy")
            return error

        # Successfuly disabled total dissolved solids output!
        return Error(None)


    def disable_salinity_output(self) -> Error:
        """ Tries to disable salinity output until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.disable_salinity_output()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.health.healthy:
            error.report("Sensor unable to disable salinity output, became too unhealthy")
            return error

        # Successfuly disabled salinity output!
        return Error(None)


    def disable_specific_gravity_output(self) -> Error:
        """ Tries to disable specific gravity output until successful or 
            becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.disable_specific_gravity_output()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.health.healthy:
            error.report("Sensor unable to disable specific gravity output, became too unhealthy")
            return error

        # Successfuly disabled specific gravity output!
        return Error(None)
