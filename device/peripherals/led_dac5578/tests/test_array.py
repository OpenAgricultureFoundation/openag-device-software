# Import standard python libraries
import sys

# Import module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.led_dac5578.array import Array
except:
    # ... if running tests from same dir as panel.py
    sys.path.append("../../../")
    from device.peripherals.led_dac5578.array import Array


panel_configs = [
    {
        "name": "Test-1",
        "bus": 2,
        "address": 0x47,
        "mux": 0x77,
        "channel": 0,
    },
    {
        "name": "Test-2",
        "bus": 2,
        "address": 0x47,
        "mux": 0x77,
        "channel": 1,
    }
]

channel_configs = [
    {
        "name": {
            "brief": "FR",
            "verbose": "Far Red"
        },
        "channel": {
            "hardware": 1,
            "software": 6
        },
        "spectrum_nm_percent": {
            "400-499": 20,
            "500-599": 80,
            "600-699": 20
        },
        "planar_distance_map": [
            {"distance_cm": 5, "intensity_watts": 100},
            {"distance_cm": 10, "intensity_watts": 50},
            {"distance_cm": 15, "intensity_watts": 25},
            {"distance_cm": 20, "intensity_watts": 12}
        ],
        "output_percent_map": [
            {"output_percent": 100, "intensity_percent": 100},
            {"output_percent": 75, "intensity_percent": 66},
            {"output_percent": 50, "intensity_percent": 33},
            {"output_percent": 25, "intensity_percent": 0},
            {"output_percent": 0, "intensity_percent": 0}
        ]
    },
    {
        "name": {
            "brief": "WW",
            "verbose": "Warm White"
        },
        "channel": {
            "hardware": 2,
            "software": 7
        },
        "spectrum_nm_percent": {
            "400-499": 20,
            "500-599": 60,
            "600-699": 20,
        },
        "planar_distance_map": [
            {"distance_cm": 5, "intensity_watts": 100},
            {"distance_cm": 10, "intensity_watts": 50},
            {"distance_cm": 15, "intensity_watts": 25},
            {"distance_cm": 20, "intensity_watts": 12}
        ],
        "output_percent_map": [
            {"output_percent": 100, "intensity_percent": 100},
            {"output_percent": 75, "intensity_percent": 66},
            {"output_percent": 50, "intensity_percent": 33},
            {"output_percent": 25, "intensity_percent": 0},
            {"output_percent": 0, "intensity_percent": 0}
        ]
    }
]

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
    array = LEDArray(
        name = "Test",
        panel_configs = panel_configs,
        channel_configs = channel_configs,
        simulate = True,
    )


def test_initialize():
    array = LEDArray("Test", panel_configs, channel_configs, simulate = True)
    array.initialize()


def test_probe():
    array = LEDArray("Test", panel_configs, channel_configs, simulate = True)

    # Standard case
    error = array.probe(retry=True)
    assert error.exists() == False


def test_set_output():
    array = LEDArray("Test", panel_configs, channel_configs, simulate = True)

    # Standard case
    error = array.set_output("FR", 92.1)
    assert error.exists() == False


def test_set_outputs_standard_case():
    array = LEDArray("Test", panel_configs, channel_configs, simulate = True)
    outputs = {"FR": 92.1, "WW": 72.2}
    error = array.set_outputs(outputs)
    assert error.exists() == False


def test_set_outputs_unknown_channel_name():
    array = LEDArray("Test", panel_configs, channel_configs, simulate = True)
    outputs = {"XX": 92.1, "WW": 72.2}
    error = array.set_outputs(outputs)
    assert error.exists() == True