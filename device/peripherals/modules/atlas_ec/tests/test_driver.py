# Import standard python libraries
import os, sys, pytest

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import peripheral driver
from device.peripherals.modules.atlas_ec.driver import AtlasECDriver
from device.peripherals.modules.atlas_ec.exceptions import TakeSinglePointCalibrationError


def test_init() -> None:
    driver = AtlasECDriver(name="Test", bus=2, address=0x77, simulate=True)


def test_read_ec() -> None:
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    ec = driver.read_ec()
    assert ec == 0.0


def test_enable_ec_output() -> None:
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    driver.enable_ec_output()


def test_disable_ec_output() -> None:
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    driver.enable_ec_output()


def test_enable_tds_output() -> None:
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    driver.enable_tds_output()


def test_disable_tds_output() -> None:
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    driver.disable_tds_output()


def test_enable_salinity_output() -> None:
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    driver.enable_salinity_output()


def test_disable_salinity_output() -> None:
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    driver.disable_salinity_output()


def test_enable_specific_gravity_output() -> None:
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    driver.enable_specific_gravity_output()


def test_disable_specific_gravity_output() -> None:
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    driver.disable_specific_gravity_output()


def test_set_probe_type() -> None:
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    driver.set_probe_type(1.0)


def test_take_dry_calibration_reading() -> None:
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    driver.take_dry_calibration_reading()


def test_take_single_point_calibration_reading() -> None:
    driver = AtlasECDriver("Test", 2, 0x77, simulate=True)
    with pytest.raises(TakeSinglePointCalibrationError):
        driver.take_single_point_calibration_reading(1.413)
