# Import standard python modules
import time, platform, subprocess

# Import python types
from typing import Dict, List, Tuple

# Import device utilities
from device.utilities import logger
from device.utilities.statemachine import manager
from device.utilities.state.main import State

# Import package elements
from device.upgrade import events, modes


class UpgradeManager(manager.StateMachineManager):
    """Manages software upgrades."""

    def __init__(self, state: State, autoupgrade: bool = False) -> None:
        """Initializes upgrade manager."""

        # Initialize parent class
        super().__init__()

        # Initialize parameters
        self.state = state
        self.autoupgrade = autoupgrade

        # Initialize logger
        self.logger = logger.Logger("Upgrade", "upgrade")
        self.logger.debug("Initializing manager")

        # Initialize state machine transitions
        self.transitions: Dict[str, List[str]] = {
            modes.AUTOMATIC: [modes.MANUAL, modes.SHUTDOWN, modes.ERROR],
            modes.MANUAL: [modes.AUTOMATIC, modes.SHUTDOWN, modes.ERROR],
            modes.ERROR: [modes.SHUTDOWN],
        }

        # Initialize state machine mode
        if self.autoupgrade:
            self.status = "Awaiting automatic check for upgrades"
            self.mode = modes.AUTOMATIC
        else:
            self.status = "Awating manual check for upgrades"
            self.mode = modes.MANUAL

    @property
    def status(self) -> str:
        """Gets value."""
        return self.state.upgrade.get("status", "None")  # type: ignore

    @status.setter
    def status(self, value: str) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.upgrade["status"] = value

    @property
    def current_version(self) -> str:
        """Gets value from shared state."""
        return self.state.upgrade.get("current_version", "Unknown")  # type: ignore

    @current_version.setter
    def current_version(self, value: str) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.upgrade["current_version"] = value

    @property
    def upgrade_version(self) -> str:
        """Gets value from shared state."""
        return self.state.upgrade.get("upgrade_version", "Unknown")  # type: ignore

    @upgrade_version.setter
    def upgrade_version(self, value: str) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.upgrade["upgrade_version"] = value

    @property
    def upgrade_available(self) -> bool:
        """Gets value from shared state."""
        return self.state.upgrade.get("upgrade_available", False)  # type: ignore

    @upgrade_available.setter
    def upgrade_available(self, value: bool) -> None:
        """Safely updates value in shared state."""
        with self.state.lock:
            self.state.upgrade["upgrade_available"] = value

    ##### STATE MACHINE FUNCTIONS ######################################################

    def run(self) -> None:
        """Runs state machine."""

        # Loop forever
        while True:

            # Check if manager is shutdown
            if self.is_shutdown:
                break

            # Check for mode transitions
            if self.mode == modes.AUTOMATIC:
                self.run_automatic_mode()
            elif self.mode == modes.MANUAL:
                self.run_manual_mode()
            elif self.mode == modes.ERROR:
                self.run_error_mode()  # defined in parent classs
            elif self.mode == modes.SHUTDOWN:
                self.run_shutdown_mode()  # defined in parent class
            else:
                self.logger.critical("Invalid state machine mode")
                self.mode = modes.INVALID
                self.is_shutdown = True
                break

    def run_automatic_mode(self) -> None:
        """Runs normal mode."""
        self.logger.debug("Entered AUTOMATIC")

        # Initialize last update time
        last_update_time = 0.0
        update_interval = 86400  # seconds -> every day

        # Loop forever
        while True:

            # Check for software update every update interval
            if time.time() - last_update_time > update_interval:
                last_update_time = time.time()

                # Check for software upgrade and upgrade if available
                self.upgrade_available = self._upgrade_available()
                if self.autoupgrade and self.upgrade_available:
                    self.upgrade_software()

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.AUTOMATIC):
                break

            # Update every 100ms
            time.sleep(0.1)

    def run_manual_mode(self) -> None:
        """Runs manual mode."""
        self.logger.debug("Entered MANUAL")

        # Initialize last update time
        last_update_time = 0.0
        update_interval = 86400  # seconds -> every day

        # Loop forever
        while True:

            # Check for events
            self.check_events()

            # Check for transitions
            if self.new_transition(modes.MANUAL):
                break

            # Update every minute
            time.sleep(60)

    ##### HELPER FUNCTIONS #############################################################

    def _upgrade_available(self) -> bool:
        """Checks for a software upgrade by updating the list of available packages then 
        getting the verison information for the openagbrain package. Takes a few minutes
        to execute."""
        message = "Checking for software upgrades"
        self.logger.debug(message)
        self.status = message

        # Update list of all available packages
        try:
            command = ["sudo", "apt-get", "update"]
            subprocess.run(command)
        except:
            message = "Unable to check for software upgrades, unable to update list of available packages"
            self.status = message
            self.logger.exception(message)
            self.mode = modes.ERROR
            return False

        # Initialize package version info
        installed_version = "Unknown"
        candidate_version = "Unknown"

        # Get package version info
        try:
            command = ["apt-cache", "policy", "openagbrain"]
            with subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as process1:
                output = process1.stdout.read().decode("utf-8")
                output += process1.stderr.read().decode("utf-8")
                lines = output.splitlines()
                for line in lines:
                    tokens = line.split()
                    for token in tokens:
                        if token.startswith("Installed:"):
                            installed_version = tokens[1]
                            break
                        elif token.startswith("Candidate:"):
                            candidate_version = tokens[1]
                            break
        except:
            message = "Unable to check for software upgrades, unable to get package version info"
            self.status = message
            self.logger.exception(message)
            self.current_version = installed_version
            self.upgrade_version = candidate_version
            self.mode = modes.ERROR
            return False

        # Update package version info in shared state
        self.current_version = installed_version
        self.upgrade_version = candidate_version

        # Verify package info is known
        if self.current_version == "Unknown" or self.upgrade_version == "Unknown":
            message = "Unable to check for software upgrades, unknown package version"
            self.status = message
            self.logger.error(message)
            self.mode = modes.ERROR
            return False

        # Check if software is up to date
        if self.current_version == self.upgrade_version:
            message = "Software is up to date"
            self.status = message
            self.logger.info(message)
            return False

        # Software update is available
        message = "Software update is available"
        self.status = message
        self.logger.info(message)
        return True

    def upgrade_software(self) -> None:
        """Upgrades our debian package to the latest version available. Writes upgrade 
        commands to a temporary file that is executed a minute later. This is necessary 
        because if we call 'sudo apt-get install -y openagbrain' from inside the django
        process we will create a deadlock where apt can't complete the install because 
        it is run as a child of the process it has to terminate."""
        self.logger.info("Upgrading software")
        self.status = "Upgrading software"

        # Create at-commands file
        try:
            filepath = "/tmp/openagbrain-at-commands"
            with open(filepath, "w") as f:
                f.write("systemctl stop rc.local\n")
                f.write("apt-get install -y openagbrain\n")
        except:
            message = "Unable to upgrade software, failed to create at-commands file"
            self.status = message
            self.logger.exception(message)
            self.mode = modes.ERROR
            return

        # Execute at commands
        try:
            command = [
                "at",
                "-f",
                "/tmp/openagbrain-at-commands",
                "now",
                "+",
                "1",
                "minute",
            ]
            subprocess.Popen(command)
            self.status = "Upgrading software, will restart in 2 minutes"
            self.upgrade_available = False
        except:
            message = "Unable to execute at-commands"
            self.status = message
            self.logger.exception(message)
            self.upgrade_available = False
            self.mode = modes.ERROR

    ##### EVENT FUNCTIONS ##############################################################

    def check(self) -> Tuple[str, int]:
        """Checks for software upgrade. Can take a few minutes."""
        self.logger.debug("Checking for software upgrade")

        # Check for upgrade
        self.upgrade_available = self._upgrade_available()

        # Check for errors
        if self.mode == modes.ERROR:
            message = "Unable to check for software upgrade"
            return message, 500

        # Successfully checked for upgrade
        message = "Successfully checked for software upgrade"
        return message, 200

    def upgrade(self) -> Tuple[str, int]:
        """Upgrades software. Can take a few minutes."""
        self.logger.debug("Upgrading software")

        # Upgrade software
        self.upgrade_software()

        # Check for errors
        if self.mode == modes.ERROR:
            message = "Unable to upgrade software"
            return message, 500

        # Successfully upgraded software
        message = "Successfully upgraded software"
        return message, 200
