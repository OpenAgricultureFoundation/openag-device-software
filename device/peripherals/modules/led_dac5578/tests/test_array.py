# Import standard python libraries
import sys, os, json

# Import module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.modules.led_dac5578.array import LEDDAC5578Array
except:
    # ... if running tests from same dir as panel.py
    sys.path.append("../../../../")
    from device.peripherals.modules.led_dac5578.array import LEDDAC5578Array

# Change directory for importing files
os.chdir("../../../../")

# Import test device config
filename = "device/peripherals/modules/led_dac5578/tests/config.json"
device_config = json.load(open(filename))
peripheral_config = device_config["peripherals"][0]
panel_configs = peripheral_config["parameters"]["communication"]["panels"]

# Import test peripheral setup
filename = "device/peripherals/modules/led_dac5578/tests/setup.json"
peripheral_setup = json.load(open(filename))
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
    "650-699": 10,
}


def test_init():
    array = LEDDAC5578Array(
        name="Test",
        panel_configs=panel_configs,
        channel_configs=channel_configs,
        simulate=True,
    )


def test_initialize():
    array = LEDDAC5578Array("Test", panel_configs, channel_configs, simulate=True)
    array.initialize()


def test_set_output():
    array = LEDDAC5578Array("Test", panel_configs, channel_configs, simulate=True)

    # Standard case
    error = array.set_output("FR", 92.1)
    assert error.exists() == False


def test_set_outputs_standard_case():
    array = LEDDAC5578Array("Test", panel_configs, channel_configs, simulate=True)
    outputs = {"FR": 92.1, "WW": 72.2}
    error = array.set_outputs(outputs)
    assert error.exists() == False


def test_set_outputs_unknown_channel_name():
    array = LEDDAC5578Array("Test", panel_configs, channel_configs, simulate=True)
    outputs = {"XX": 92.1, "WW": 72.2}
    error = array.set_outputs(outputs)
    assert error.exists() == True


def test_set_spd():
    array = LEDDAC5578Array("Test", panel_configs, channel_configs, simulate=True)
    channel_outputs, output_spectrum_nm_percent, output_intensity_watts, error = array.set_spd(
        desired_distance_cm=desired_distance_cm,
        desired_intensity_watts=desired_intensity_watts,
        desired_spectrum_nm_percent=desired_spectrum_nm_percent,
    )
    assert error.exists() == False
    assert channel_outputs == {"FR": 46.0, "WW": 54.0}
    assert output_spectrum_nm_percent == {
        "400-449": 12.27,
        "449-499": 12.27,
        "500-549": 42.44,
        "550-559": 8.49,
        "600-649": 12.27,
        "650-699": 12.27,
    }
    assert output_intensity_watts == 81.52


def test_set_spd_flat_taurus():

    # Load in channel configs
    filename = "device/peripherals/modules/led_dac5578/setups/taurus.json"
    peripheral_setup = json.load(open(filename))
    channel_configs = peripheral_setup["channel_configs"]

    # Initialize array
    array = LEDDAC5578Array("Test", panel_configs, channel_configs, simulate=True)

    # Set desired setpoints
    spectrum_flat = {
        "400-449": 16.67,
        "449-499": 16.67,
        "500-549": 16.67,
        "550-559": 16.67,
        "600-649": 16.67,
        "650-699": 16.67,
    }

    # Set expected outputs
    expected_channel_outputs = {
        "WW": 0.0,
        "CW": 0.0,
        "B": 33.0,
        "G": 38.0,
        "R": 33.0,
        "FR": 0.0,
    }
    expected_output_spectrum = {
        "400-449": 18.58,
        "449-499": 18.58,
        "500-549": 21.4,
        "550-559": 4.28,
        "600-649": 18.58,
        "650-699": 18.58,
    }
    expected_output_intensity = 88.8

    # Set SPD
    channel_outputs, output_spectrum, output_intensity, error = array.set_spd(
        desired_distance_cm=desired_distance_cm,
        desired_intensity_watts=desired_intensity_watts,
        desired_spectrum_nm_percent=spectrum_flat,
    )

    # Evaluate results
    assert error.exists() == False
    assert channel_outputs == expected_channel_outputs
    assert output_spectrum == expected_output_spectrum
    assert output_intensity == expected_output_intensity


def test_set_spd_blue_taurus():

    # Load in channel configs
    filename = "device/peripherals/modules/led_dac5578/setups/taurus.json"
    peripheral_setup = json.load(open(filename))
    channel_configs = peripheral_setup["channel_configs"]

    # Initialize array
    array = LEDDAC5578Array("Test", panel_configs, channel_configs, simulate=True)

    # Set desired setpoints
    spectrum_flat = {
        "400-449": 50,
        "449-499": 50,
        "500-549": 0,
        "550-559": 0,
        "600-649": 0,
        "650-699": 0,
    }

    # Set expected outputs
    expected_channel_outputs = {
        "WW": 0.0,
        "CW": 0.0,
        "B": 100.0,
        "G": 0.0,
        "R": 0.0,
        "FR": 0.0,
    }
    expected_output_spectrum = {
        "400-449": 50.0,
        "449-499": 50.0,
        "500-549": 0.0,
        "550-559": 0.0,
        "600-649": 0.0,
        "650-699": 0.0,
    }
    expected_output_intensity = 100.0

    # Set SPD
    channel_outputs, output_spectrum, output_intensity, error = array.set_spd(
        desired_distance_cm=desired_distance_cm,
        desired_intensity_watts=desired_intensity_watts,
        desired_spectrum_nm_percent=spectrum_flat,
    )

    # Print results
    print(channel_outputs)
    print(output_spectrum)
    print(output_intensity)

    # Evaluate results
    assert error.exists() == False
    assert channel_outputs == expected_channel_outputs
    assert output_spectrum == expected_output_spectrum
    assert output_intensity == expected_output_intensity

    def test_set_spd_blue_taurus():

        # Load in channel configs
        filename = "device/peripherals/modules/led_dac5578/setups/taurus.json"
        peripheral_setup = json.load(open(filename))
        channel_configs = peripheral_setup["channel_configs"]

        # Initialize array
        array = LEDDAC5578Array("Test", panel_configs, channel_configs, simulate=True)

        # Set desired setpoints
        spectrum_flat = {
            "400-449": 50,
            "449-499": 50,
            "500-549": 0,
            "550-559": 0,
            "600-649": 0,
            "650-699": 0,
        }

        # Set expected outputs
        expected_channel_outputs = {
            "WW": 0.0,
            "CW": 0.0,
            "B": 100.0,
            "G": 0.0,
            "R": 0.0,
            "FR": 0.0,
        }
        expected_output_spectrum = {
            "400-449": 50.0,
            "449-499": 50.0,
            "500-549": 0.0,
            "550-559": 0.0,
            "600-649": 0.0,
            "650-699": 0.0,
        }
        expected_output_intensity = 100.0

        # Set SPD
        channel_outputs, output_spectrum, output_intensity, error = array.set_spd(
            desired_distance_cm=desired_distance_cm,
            desired_intensity_watts=desired_intensity_watts,
            desired_spectrum_nm_percent=spectrum_flat,
        )

        # Print results
        print(channel_outputs)
        print(output_spectrum)
        print(output_intensity)

        # Evaluate results
        assert error.exists() == False
        assert channel_outputs == expected_channel_outputs
        assert output_spectrum == expected_output_spectrum
        assert output_intensity == expected_output_intensity


def test_set_spd_green_taurus():

    # Load in channel configs
    filename = "device/peripherals/modules/led_dac5578/setups/taurus.json"
    peripheral_setup = json.load(open(filename))
    channel_configs = peripheral_setup["channel_configs"]

    # Initialize array
    array = LEDDAC5578Array("Test", panel_configs, channel_configs, simulate=True)

    # Set desired setpoints
    spectrum_flat = {
        "400-449": 0,
        "449-499": 0,
        "500-549": 50,
        "550-559": 50,
        "600-649": 0,
        "650-699": 0,
    }

    # Set expected outputs
    expected_channel_outputs = {
        "WW": 0.0,
        "CW": 0.0,
        "B": 0.0,
        "G": 100.0,
        "R": 0.0,
        "FR": 0.0,
    }
    expected_output_spectrum = {
        "400-449": 0.0,
        "449-499": 0.0,
        "500-549": 83.33,
        "550-559": 16.67,
        "600-649": 0.0,
        "650-699": 0.0,
    }
    expected_output_intensity = 60.0

    # Set SPD
    channel_outputs, output_spectrum, output_intensity, error = array.set_spd(
        desired_distance_cm=desired_distance_cm,
        desired_intensity_watts=desired_intensity_watts,
        desired_spectrum_nm_percent=spectrum_flat,
    )

    # Print results
    print(channel_outputs)
    print(output_spectrum)
    print(output_intensity)

    # Evaluate results
    assert error.exists() == False
    assert channel_outputs == expected_channel_outputs
    assert output_spectrum == expected_output_spectrum
    assert output_intensity == expected_output_intensity


def test_set_spd_red_taurus():

    # Load in channel configs
    filename = "device/peripherals/modules/led_dac5578/setups/taurus.json"
    peripheral_setup = json.load(open(filename))
    channel_configs = peripheral_setup["channel_configs"]

    # Initialize array
    array = LEDDAC5578Array("Test", panel_configs, channel_configs, simulate=True)

    # Set desired setpoints
    spectrum_flat = {
        "400-449": 0,
        "449-499": 0,
        "500-549": 0,
        "550-559": 0,
        "600-649": 50,
        "650-699": 50,
    }

    # Set expected outputs
    expected_channel_outputs = {
        "WW": 0.0,
        "CW": 0.0,
        "B": 0.0,
        "G": 0.0,
        "R": 100.0,
        "FR": 0.0,
    }
    expected_output_spectrum = {
        "400-449": 0.0,
        "449-499": 0.0,
        "500-549": 0.0,
        "550-559": 0.0,
        "600-649": 50.0,
        "650-699": 50.0,
    }
    expected_output_intensity = 100.0

    # Set SPD
    channel_outputs, output_spectrum, output_intensity, error = array.set_spd(
        desired_distance_cm=desired_distance_cm,
        desired_intensity_watts=desired_intensity_watts,
        desired_spectrum_nm_percent=spectrum_flat,
    )

    # Print results
    print(channel_outputs)
    print(output_spectrum)
    print(output_intensity)

    # Evaluate results
    assert error.exists() == False
    assert channel_outputs == expected_channel_outputs
    assert output_spectrum == expected_output_spectrum
    assert output_intensity == expected_output_intensity
