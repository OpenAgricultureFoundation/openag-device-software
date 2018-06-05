# Import standard python libraries
import sys, os, json

# Import module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.led_dac5578.array import Array
except:
    # ... if running tests from same dir as panel.py
    sys.path.append("../../../../")
    from device.peripherals.modules.led_dac5578.array import Array

# Change directory for importing files
os.chdir("../../../../")

# Import test device config
device_config = json.load(open("device/peripherals/modules/led_dac5578/tests/config.json"))
peripheral_config = device_config["peripherals"][0]
panel_configs = peripheral_config["parameters"]["communication"]["panels"]

# Import test peripheral setup
peripheral_setup = json.load(open("device/peripherals/modules/led_dac5578/tests/setup.json"))
channel_configs = peripheral_setup["channel_configs"]

# Initialize test desired spd
desired_distance_cm = 5
desired_intensity_watts = 100
desired_spectrum_nm_percent = {
    "400-449": 10,
    "449-499": 10,
    "500-549": 30, 
    "550-559": 30,
    "600-649": 10,
    "650-699": 10}


def test_init():
    array = Array(
        name = "Test",
        panel_configs = panel_configs,
        channel_configs = channel_configs,
        simulate = True,
    )


def test_initialize():
    array = Array("Test", panel_configs, channel_configs, simulate = True)
    array.initialize()


def test_set_output():
    array = Array("Test", panel_configs, channel_configs, simulate = True)

    # Standard case
    error = array.set_output("FR", 92.1)
    assert error.exists() == False


def test_set_outputs_standard_case():
    array = Array("Test", panel_configs, channel_configs, simulate = True)
    outputs = {"FR": 92.1, "WW": 72.2}
    error = array.set_outputs(outputs)
    assert error.exists() == False


def test_set_outputs_unknown_channel_name():
    array = Array("Test", panel_configs, channel_configs, simulate = True)
    outputs = {"XX": 92.1, "WW": 72.2}
    error = array.set_outputs(outputs)
    assert error.exists() == True


def test_set_spd():
    array = Array("Test", panel_configs, channel_configs, simulate = True)
    channel_outputs, output_spectrum_nm_percent, output_intensity_watts, error = array.set_spd(
        desired_distance_cm = desired_distance_cm, 
        desired_intensity_watts = desired_intensity_watts, 
        desired_spectrum_nm_percent = desired_spectrum_nm_percent,
    )
    assert error.exists() == False
    assert channel_outputs == {'FR': 46.0, 'WW': 54.0}
    assert output_spectrum_nm_percent == {'400-449': 12.27, '449-499': 12.27, '500-549': 42.44, '550-559': 8.49, '600-649': 12.27, '650-699': 12.27}
    assert output_intensity_watts == 81.52