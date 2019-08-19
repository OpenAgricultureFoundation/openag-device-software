# Import standard python modules
import os, sys, threading

# Import python types
from typing import Any, Dict

# Set system path
sys.path.append(str(os.getenv("PROJECT_ROOT", "")))


# Import run peripheral parent class
from device.peripherals.classes.peripheral.scripts.run_peripheral import RunnerBase

# Import peripheral driver
from device.peripherals.common.adt7470.driver import ADT7470Driver


class DriverRunner(RunnerBase):  # type: ignore
    """Runs driver."""

    # Initialize defaults
    default_device = "pfc4-v0.1.0"
    default_name = "HeatSinkFanController"

    # Initialize var types
    communication: Dict[str, Any]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes run driver."""

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Initialize parser
        self.parser.add_argument("--version", action="store_true", help="read version")
        self.parser.add_argument(
            "--enable-manual-fan-control", type=int, help="enable manual fan control"
        )
        self.parser.add_argument(
            "--enable-automatic-fan-control",
            type=int,
            help="enable automatic fan control",
        )
        self.parser.add_argument(
            "--write-minimum-duty-cycle",
            type=int,
            help="write minimum duty cycle for a fan",
            nargs="+",
        )
        self.parser.add_argument(
            "--write-maximum-duty-cycle",
            type=int,
            help="write maximum duty cycle for a fan",
            nargs="+",
        )
        self.parser.add_argument(
            "--write-current-duty-cycle",
            type=int,
            help="write current duty cycle for a fan",
            nargs="+",
        )
        self.parser.add_argument(
            "--write-fan-pulses-per-revolution",
            type=int,
            help="write the number of fan pulses per revolution",
            nargs="+",
        )
        self.parser.add_argument("--read-fan-speed", type=int, help="read fan speed")
        self.parser.add_argument("--read-current-duty-cycle", type=int, help="read current duty cycle")
        self.parser.add_argument(
            "--write-thermal-zone-config",
            type=int,
            help="write thermal zone config",
            nargs="+",
        )
        self.parser.add_argument(
            "--write-thermal-zone-minimum-temperature",
            type=int,
            help="write thermal zone minimum temperature",
            nargs="+",
        )
        self.parser.add_argument(
            "--enable-monitoring",
            action="store_true",
            help="enable temperature monitoring",
        )
        self.parser.add_argument(
            "--disable-monitoring",
            action="store_true",
            help="disable temperature monitoring",
        )
        self.parser.add_argument(
            "--enable-high-frequency-fan-drive",
            action="store_true",
            help="enable high frequency fan drive",
        )
        self.parser.add_argument(
            "--enable-low-frequency-fan-drive",
            action="store_true",
            help="enable low frequency fan drive",
        )
        self.parser.add_argument(
            "--read-temperature", type=int, help="read temperature"
        )
        self.parser.add_argument(
            "--read-maximum-temperature",
            action="store_true",
            help="read maximum temperature",
        )
        self.parser.add_argument(
            "--write-temperature-limits",
            action="store_true",
            help="write temperature limits",
        )
        self.parser.add_argument(
            "--shutdown", action="store_true", help="shutdown hardware"
        )

    def run(self, *args: Any, **kwargs: Any) -> None:
        """Runs driver."""

        # Run parent class
        super().run(*args, **kwargs)

        # Initialize driver
        self.driver = ADT7470Driver(
            name=self.args.name,
            i2c_lock=threading.RLock(),
            bus=self.bus,
            address=self.address,
            mux=self.mux,
            channel=self.channel,
        )

        # Check if reading version
        if self.args.version:
            self.driver.read_version()

        # Check if enabling manual fan control
        elif self.args.enable_manual_fan_control != None:
            self.driver.enable_manual_fan_control(self.args.enable_manual_fan_control)

        # Check if enabling automatic fan control
        elif self.args.enable_automatic_fan_control != None:
            self.driver.enable_automatic_fan_control(
                self.args.enable_automatic_fan_control
            )
        
        # Check if writing minimum duty cycle
        elif self.args.write_minimum_duty_cycle != None:
            fan_id = self.args.write_minimum_duty_cycle[0]
            duty_cycle = self.args.write_minimum_duty_cycle[1]
            self.driver.write_minimum_duty_cycle(fan_id, duty_cycle)
        
        # Check if writing maximum duty cycle
        elif self.args.write_maximum_duty_cycle != None:
            fan_id = self.args.write_maximum_duty_cycle[0]
            duty_cycle = self.args.write_maximum_duty_cycle[1]
            self.driver.write_maximum_duty_cycle(fan_id, duty_cycle)
        
        # Check if writing current duty cycle
        elif self.args.write_current_duty_cycle != None:
            fan_id = self.args.write_current_duty_cycle[0]
            duty_cycle = self.args.write_current_duty_cycle[1]
            self.driver.write_current_duty_cycle(fan_id, duty_cycle)

        # Check if writing fan pulses per revolution
        elif self.args.write_fan_pulses_per_revolution != None:
            fan_id = self.args.write_fan_pulses_per_revolution[0]
            pulses_per_revolution = self.args.write_fan_pulses_per_revolution[1]
            self.driver.write_fan_pulses_per_revolution(fan_id, pulses_per_revolution)

        # Check if reading fan speed
        elif self.args.read_fan_speed != None:
            self.driver.read_fan_speed(self.args.read_fan_speed)
        
        # Check if reading duty cycle
        elif self.args.read_current_duty_cycle != None:
            self.driver.read_current_duty_cycle(self.args.read_current_duty_cycle)

        # Check if writing thermal zone config
        elif self.args.write_thermal_zone_config != None:
            fan_id = self.args.write_thermal_zone_config[0]
            if self.args.write_thermal_zone_config[1] == -1:
                sensor_id = "max"
            else:
                sensor_id = self.args.write_thermal_zone_config[1]
            self.driver.write_thermal_zone_config(fan_id, sensor_id)

        # Check if writing thermal zone minimum temperature
        elif self.args.write_thermal_zone_minimum_temperature != None:
            fan_id = self.args.write_thermal_zone_minimum_temperature[0]
            temperature = self.args.write_thermal_zone_minimum_temperature[1]
            self.driver.write_thermal_zone_minimum_temperature(fan_id, temperature)

        # Check if enabling monitoring
        elif self.args.enable_monitoring:
            self.driver.enable_monitoring()

        # Check if disabling monitoring
        elif self.args.disable_monitoring:
            self.driver.disable_monitoring()

        # Check if reading temperature
        elif self.args.read_temperature != None:
            self.driver.read_temperature(self.args.read_temperature)

        # Check if reading max temperature
        elif self.args.read_maximum_temperature:
            self.driver.read_maximum_temperature()

        # Check if writing temperature limits
        elif self.args.write_temperature_limits:
            self.driver.write_temperature_limits(0, 0, 40)

        # Check if enabling high frequency fan drive
        elif self.args.enable_high_frequency_fan_drive:
            self.driver.enable_high_frequency_fan_drive()

        # Check if enabling low frequency fan drive
        elif self.args.enable_low_frequency_fan_drive:
            self.driver.enable_low_frequency_fan_drive()

        # Check if shutting down
        elif self.args.shutdown:
            self.driver.shutdown()


# Run main
if __name__ == "__main__":
    driver_runner = DriverRunner()
    driver_runner.run()

"""
Fan Verification & Calibration
1. enable-manual-fan-control <fan_id>
2. write-current-duty-cycle <fan_id> 100
3. read-fan-speed <fan_id>
4. Repeat step 2 to find min & max duty cycles
"""
