# Import standard python libraries
import os, sys, pytest, json, numpy

# Set system path
root_dir = os.environ["PROJECT_ROOT"]
sys.path.append(root_dir)
os.chdir(root_dir)

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import peripheral driver
from device.peripherals.utilities import light

# Load orion orion_properties
print(os.getcwd())
orion_setup = json.load(
    open("device/peripherals/modules/led_dac5578/setups/orion-v1.json")
)
orion_properties = orion_setup["properties"]
taurus_setup = json.load(
    open("device/peripherals/modules/led_dac5578/setups/taurus-v1.json")
)
taurus_properties = taurus_setup["properties"]


def test_calculate_spd_dict() -> None:
    intensity = 200
    spectrum = {"380-399": 0, "400-499": 33, "500-599": 33, "600-700": 34, "701-780": 0}
    expected = {"380-399": 0, "400-499": 66, "500-599": 66, "600-700": 68, "701-780": 0}
    spd_dict = light.calculate_spd_dict(intensity, spectrum)
    assert spd_dict == expected


def test_get_intensity_at_distance() -> None:
    intensity_map = {"0": 200, "5": 150, "10": 100, "15": 50}
    distance = 10
    cumulative_intensity = light.get_intensity_at_distance(intensity_map, distance)
    assert cumulative_intensity == 100


def test_build_channel_spd_ndict() -> None:
    props = {
        "channels": {
            "A": {"name": "A", "type": "A", "port": 0},
            "B1": {"name": "B1", "type": "B", "port": 1},
            "B2": {"name": "B2", "type": "B", "port": 2},
        },
        "intensity_map_cm_umol": {"0": 200, "5": 150, "10": 100, "15": 50},
        "channel_types": {
            "A": {
                "name": "A",
                "relative_intensity_percent": 20,
                "spectrum_nm_percent": {
                    "380-399": 10,
                    "400-499": 10,
                    "500-599": 10,
                    "600-700": 10,
                    "701-780": 60,
                },
                "logic_scaler_percents": {
                    "0": 0,
                    "25": 12.5,
                    "50": 25,
                    "75": 37.5,
                    "100": 50,
                },
            },
            "B": {
                "name": "B",
                "relative_intensity_percent": 40,
                "spectrum_nm_percent": {
                    "380-399": 20,
                    "400-499": 20,
                    "500-599": 20,
                    "600-700": 20,
                    "701-780": 20,
                },
                "logic_scaler_percents": {
                    "0": 0,
                    "25": 12.5,
                    "50": 25,
                    "75": 37.5,
                    "100": 50,
                },
            },
        },
    }
    distance = 10
    channel_spd_ndict = light.build_channel_spd_ndict(props, distance)
    expected = {
        "A": {
            "380-399": 2.0,
            "400-499": 2.0,
            "500-599": 2.0,
            "600-700": 2.0,
            "701-780": 12.0,
        },
        "B": {
            "380-399": 16.0,
            "400-499": 16.0,
            "500-599": 16.0,
            "600-700": 16.0,
            "701-780": 16.0,
        },
    }
    assert channel_spd_ndict == expected


def test_calculate_output_spd() -> None:
    channel_spd_matrix = numpy.array([[1, 2], [3, 4]])
    channel_output_vector = [1, 0.5]
    expected = [2, 5]
    output_spd_list = light.calculate_output_spd(
        channel_spd_matrix, channel_output_vector
    )
    assert output_spd_list == expected


def test_deconstruct_spd() -> None:
    spd_list = [40, 60, 100]
    expected_spectrum_list = [20, 30, 50]
    expected_intensity = 200
    spectrum_list, intensity = light.deconstruct_spd(spd_list)
    assert spectrum_list == expected_spectrum_list
    assert intensity == expected_intensity


def test_calculate_resultant_spd() -> None:
    props = {
        "channels": {
            "A": {"name": "A", "type": "A", "port": 0},
            "B1": {"name": "B1", "type": "B", "port": 1},
            "B2": {"name": "B2", "type": "B", "port": 2},
        },
        "intensity_map_cm_umol": {"0": 200, "5": 150, "10": 100, "15": 50},
        "channel_types": {
            "A": {
                "name": "A",
                "relative_intensity_percent": 50,
                "spectrum_nm_percent": {
                    "380-399": 20,
                    "400-499": 20,
                    "500-599": 20,
                    "600-700": 20,
                    "701-780": 20,
                },
            },
            "B": {
                "name": "B",
                "relative_intensity_percent": 25,
                "spectrum_nm_percent": {
                    "380-399": 20,
                    "400-499": 20,
                    "500-599": 20,
                    "600-700": 20,
                    "701-780": 20,
                },
            },
        },
    }
    distance = 10
    # channel_spd_ndict = light.build_channel_spd_ndict(props, distance)
    setpoints = {"A": 100, "B1": 100, "B2": 100}
    reference_spectrum = {
        "380-399": 2.0,
        "400-499": 2.0,
        "500-599": 2.0,
        "600-700": 2.0,
        "701-780": 12.0,
    }
    expected_spectrum = {
        "380-399": 20,
        "400-499": 20,
        "500-599": 20,
        "600-700": 20,
        "701-780": 20,
    }
    expected_intensity = 100

    spectrum, intensity = light.calculate_resultant_spd(
        props, reference_spectrum, setpoints, distance
    )
    assert spectrum == expected_spectrum
    assert intensity == expected_intensity


# def test_calculate_ulrf_orion_1600_par() -> None:
#     desired_distance = 4
#     setpoints = {"FR": 100, "CW1": 100, "CW2": 100, "CW3": 100, "CW4": 100, "WW": 100}
#     expected_spectrum = {
#         "380-399": 0.0,
#         "400-499": 19.56,
#         "500-599": 39.61,
#         "600-700": 35.22,
#         "701-780": 5.6,
#     }
#     expected_intensity = 1650.81
#     expected_distance = 4
#     spectrum, intensity, distance = light.calculate_ulrf_from_percents(
#         orion_properties, setpoints, desired_distance
#     )
#     print(spectrum, intensity, distance)
#     assert spectrum == expected_spectrum
#     assert intensity == expected_intensity
#     assert distance == expected_distance


# def test_approximate_spd_orion_1600_par() -> None:
#     distance = 4.0
#     desired_intensity = 1600.0
#     desired_spectrum = {
#         "380-399": 0.0,
#         "400-499": 19.56,
#         "500-599": 39.61,
#         "600-700": 35.22,
#         "701-780": 5.6,
#     }
#     expected_spectrum = desired_spectrum
#     expected_intensity = 1599.59
#     expected_setpoints = {
#         "FR": 96.6, "WW": 96.9, "CW1": 96.9, "CW2": 96.9, "CW3": 96.9, "CW4": 96.9
#     }
#     setpoints, spectrum, intensity = light.approximate_spd(
#         orion_properties, distance, desired_intensity, desired_spectrum
#     )
#     print(intensity, setpoints, spectrum)
#     assert setpoints == expected_setpoints
#     assert spectrum == expected_spectrum
#     assert intensity == expected_intensity


# def test_calculate_ulrf_taurus_1500_par() -> None:
#     desired_distance = 4
#     setpoints = {"FR": 100, "R": 100, "G": 100, "B": 100, "CW": 100, "WW": 100}
#     expected_spectrum = {
#         "380-399": 0.0,
#         "400-499": 28.01,
#         "500-599": 26.9,
#         "600-700": 41.13,
#         "701-780": 3.96,
#     }
#     expected_intensity = 1481.74
#     expected_distance = desired_distance
#     spectrum, intensity, distance = light.calculate_ulrf_from_percents(
#         taurus_properties, setpoints, desired_distance
#     )
#     print(spectrum, intensity, distance)
#     assert spectrum == expected_spectrum
#     assert intensity == expected_intensity
#     assert distance == expected_distance


# def test_approximate_spd_taurus_1500_par() -> None:
#     distance = 4
#     desired_intensity = 1481.74
#     desired_spectrum = {
#         "380-399": 0.0,
#         "400-499": 28.01,
#         "500-599": 26.9,
#         "600-700": 41.13,
#         "701-780": 3.96,
#     }
#     expected_spectrum = desired_spectrum
#     expected_intensity = desired_intensity
#     expected_setpoints = {
#         "FR": 100, "R": 100, "G": 100, "B": 100.0, "CW": 100, "WW": 100
#     }
#     setpoints, spectrum, intensity = light.approximate_spd(
#         taurus_properties, distance, desired_intensity, desired_spectrum
#     )
#     print(intensity, setpoints, spectrum)
#     assert setpoints == expected_setpoints
#     assert spectrum == expected_spectrum
#     assert intensity == expected_intensity
