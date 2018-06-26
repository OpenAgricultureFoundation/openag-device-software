# Import standard python modules
from typing import Tuple, Optional

# Import device utilities
from device.utilities.error import Error


class AtlasSensorMixin:
    """ Atlas sensor mixin for common functions across atlas sensors. """

    @property
    def healthy(self):
        return self.health.healthy

    def enable_led(self) -> Error:
        """ Tries to enable protocol lock until successful or becomes too unhealthy. """

        # Send commands until success or becomes too healthy
        while self.healthy:

            # Send command
            error = self.driver.enable_led()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to enable led, became too unhealthy")
            return error

        # Successfuly enabled led!
        return Error(None)

    def disable_led(self) -> Error:
        """ Tries to disable protocol lock until successful or becomes too unhealthy. """

        # Send commands until success or becomes too healthy
        while self.healthy:

            # Send command
            error = self.driver.disable_led()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to disable led, became too unhealthy")
            return error

        # Successfuly disables led!
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
        if not self.healthy:
            error.report("Sensor unable to enable protocol lock, became too unhealthy")
            return error

        # Successfuly enabled protocol lock!
        return Error(None)

    def disable_protocol_lock(self) -> Error:
        """ Tries to disable protocol lock until successful or becomes too unhealthy. """

        # Send commands until success of becomes too healthy
        while self.healthy:

            # Send probe
            error = self.driver.disable_protocol_lock()

            # Check for errors:
            if error.exists():
                self.health.report_failure()
            else:
                self.health.report_success()
                break

        # Check if sensor became unhealthy
        if not self.healthy:
            error.report("Sensor unable to disable protocol lock, became too unhealthy")
            return error

        # Successfuly disables protocol lock!
        return Error(None)
