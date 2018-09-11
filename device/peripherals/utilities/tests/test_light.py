# Import standard python libraries
import os, sys, pytest, json, numpy

# Set system path
root_dir = os.environ["OPENAG_BRAIN_ROOT"]
sys.path.append(root_dir)
os.chdir(root_dir)

# Import device utilities
from device.utilities.accessors import get_peripheral_config

# Import peripheral driver
from device.peripherals.utilities import light

# Load orion properties
setup = json.load(open("device/peripherals/modules/led_dac5578/setups/orion.json"))
properties = setup["properties"]


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
                    "0": 0, "25": 12.5, "50": 25, "75": 37.5, "100": 50
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
                    "0": 0, "25": 12.5, "50": 25, "75": 37.5, "100": 50
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


def test_approximate_spd_orion_1600_par() -> None:
    distance = 4.0
    desired_intensity = 1600.0
    desired_spectrum = {
        "380-399": 0.0,
        "400-499": 19.56,
        "500-599": 39.61,
        "600-700": 35.22,
        "701-780": 5.6,
    }
    expected_spectrum = desired_spectrum
    expected_intensity = 1599.59
    expected_setpoints = {
        "FR": 96.6, "WW": 96.9, "CW1": 96.9, "CW2": 96.9, "CW3": 96.9, "CW4": 96.9
    }
    setpoints, spectrum, intensity = light.approximate_spd(
        properties, distance, desired_intensity, desired_spectrum
    )
    print(intensity, setpoints, spectrum)
    assert setpoints == expected_setpoints
    assert spectrum == expected_spectrum
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
        "380-399": 2.0, "400-499": 2.0, "500-599": 2.0, "600-700": 2.0, "701-780": 12.0
    }
    expected_spectrum = {
        "380-399": 20, "400-499": 20, "500-599": 20, "600-700": 20, "701-780": 20
    }
    expected_intensity = 100

    spectrum, intensity = light.calculate_resultant_spd(
        props, reference_spectrum, setpoints, distance
    )
    assert spectrum == expected_spectrum
    assert intensity == expected_intensity


def test_calculate_ulrf_orion_1600_par() -> None:
    desired_distance = 4
    setpoints = {"FR": 100, "CW1": 100, "CW2": 100, "CW3": 100, "CW4": 100, "WW": 100}
    expected_spectrum = {
        "380-399": 0.0,
        "400-499": 19.56,
        "500-599": 39.61,
        "600-700": 35.22,
        "701-780": 5.6,
    }
    expected_intensity = 1650.81
    expected_distance = 4
    spectrum, intensity, distance = light.calculate_ulrf_from_percents(
        properties, setpoints, desired_distance
    )
    assert spectrum == expected_spectrum
    assert intensity == expected_intensity
    assert distance == expected_distance


# def test_get_ppfd_at_distance_exact():
#     ppfd = light.get_ppfd_at_distance(channel_config=channel_configs[0], distance=4)
#     assert ppfd == 34
#     ppfd = light.get_ppfd_at_distance(channel_config=channel_configs[0], distance=10)
#     assert ppfd == 16
#     ppfd = light.get_ppfd_at_distance(channel_config=channel_configs[0], distance=18)
#     assert ppfd == 8


# def test_get_ppfd_at_distance_inner_interpolate():
#     ppfd = light.get_ppfd_at_distance(channel_config=channel_configs[0], distance=6)
#     assert ppfd == 28
#     ppfd = light.get_ppfd_at_distance(channel_config=channel_configs[0], distance=14)
#     assert ppfd == 12


# def test_get_ppfd_at_distance_outer_interpolate():
#     ppfd = light.get_ppfd_at_distance(channel_config=channel_configs[0], distance=3)
#     assert ppfd == 34
#     ppfd = light.get_ppfd_at_distance(channel_config=channel_configs[0], distance=19)
#     assert ppfd == 8


# def test_discretize_spd():
#     spd = {"380-399": 0, "400-499": 208, "500-599": 176, "600-700": 312, "701-780": 104}
#     dspd = light.discretize_spd(spd)

#     # Round all values to 2 decimals
#     for key in dspd.keys():
#         dspd[key] = round(dspd[key], 2)

#     # Check min, middle, max values for each band
#     assert (dspd[380], dspd[390], dspd[399]) == (0, 0, 0)
#     assert (dspd[400], dspd[450], dspd[499]) == (2.08, 2.08, 2.08)
#     assert (dspd[500], dspd[550], dspd[599]) == (1.76, 1.76, 1.76)
#     assert (dspd[600], dspd[650], dspd[700]) == (3.09, 3.09, 3.09)
#     assert (dspd[701], dspd[750], dspd[780]) == (1.3, 1.3, 1.3)


# def translate_spd():
#     from_spd = {"300-399": 50, "400-499": 50}
#     to_spd = {"300-349": 0, "350-399": 0, "400-449": 0, "450-499": 0}
#     translated_spd = light.translage_spd(from_spd, to_spd)
#     expected_spd = {"300-349": 25, "350-399": 25, "400-449": 25, "450-499": 25}
#     assert translated_spd == expected_spd


# def test_build_channel_spd_matrix():
#     desired_spd = {
#         "380-399": 0, "400-499": 208, "500-599": 176, "600-700": 312, "701-780": 104
#     }

#     channel_spd_matrix = light.build_channel_spd_matrix(
#         channel_configs=channel_configs,
#         distance=desired_distance_cm,
#         reference_spd=desired_spd,
#     )

#     # Calculated by multiplying spectral percent * ppfd@distance
#     fr = [0, 0, 0, 1.92, 14.08]
#     r = [0, 0, 0, 222.46, 4.54]
#     g = [0, 7, 62.3, 0.7, 0]
#     b = [0, 198, 2, 0, 0]
#     cw = [0, 40.94, 83.66, 48.06, 5.34]
#     ww = [0, 15.84, 75.24, 97.02, 9.9]
#     matrix = numpy.array([fr, r, g, b, cw, ww])
#     expected_spd_matrix = numpy.transpose(matrix)

#     # Check expexted matches output
#     assert channel_spd_matrix.tolist() == expected_spd_matrix.tolist()


# def test_build_desired_spd_vector():
#     desired_spd_vector = light.build_desired_spd_vector(
#         desired_spectrum_nm_percent=desired_spectrum_nm_percent,
#         desired_ppfd_umol_m2_s=desired_ppfd_umol_m2_s,
#     )
#     assert desired_spd_vector.tolist() == [0, 208, 176, 312, 104]


# def test_calculate_channel_output_vector():
#     desired_spd_vector = light.build_desired_spd_vector(
#         desired_spectrum_nm_percent=desired_spectrum_nm_percent,
#         desired_ppfd_umol_m2_s=desired_ppfd_umol_m2_s,
#     )
#     desired_spd = {
#         "380-399": 0, "400-499": 208, "500-599": 176, "600-700": 312, "701-780": 104
#     }
#     channel_spd_matrix = light.build_channel_spd_matrix(
#         channel_configs=channel_configs,
#         distance=desired_distance_cm,
#         reference_spd=desired_spd,
#     )
#     channel_outputs = light.calculate_channel_output_vector(
#         channel_spd_matrix=channel_spd_matrix, desired_spd_vector=desired_spd_vector
#     )

#     assert channel_outputs == [1, 0.75, 0.25, 0.75, 1, 1]


# def test_approximate_spd_orion_800_par() -> None:

#     # Load orion channel configs
#     peripheral_setup = json.load(
#         open("device/peripherals/modules/led_dac5578/setups/orion.json")
#     )
#     channel_configs = peripheral_setup["channel_configs"]

#     # Set desired parameters
#     distance = 73.0
#     ppfd = 800.0
#     spectrum = {
#         "380-399": 0, "400-499": 18, "500-599": 32, "600-700": 36, "701-780": 14
#     }

#     # Approximate spd
#     channel_outputs, output_spectrum, output_ppfd = light.approximate_spd(
#         channel_configs=channel_configs,
#         desired_distance_cm=distance,
#         desired_ppfd_umol_m2_s=ppfd,
#         desired_spectrum_nm_percent=spectrum,
#     )

#     # Set expected results
#     expected_channel_outputs = {
#         "FR": 100.0, "CW1": 100.0, "CW2": 100.0, "CW3": 100.0, "CW4": 100.0, "WW": 100.0
#     }
#     expected_output_spectrum = {
#         "380-399": 0.0,
#         "400-499": 19.43,
#         "500-599": 39.5,
#         "600-700": 35.33,
#         "701-780": 5.74,
#     }
#     expected_output_ppfd = 548.52

#     # Check results match expectations
#     assert channel_outputs == expected_channel_outputs
#     assert output_spectrum == expected_output_spectrum
#     assert output_ppfd == expected_output_ppfd


# def test_approximate_spd_orion_1400_par() -> None:

#     # Load orion channel configs
#     peripheral_setup = json.load(
#         open("device/peripherals/modules/led_dac5578/setups/orion.json")
#     )
#     channel_configs = peripheral_setup["channel_configs"]

#     # Set desired parameters
#     distance = 10.0
#     ppfd = 1400.0
#     spectrum = {
#         "380-399": 0, "400-499": 18, "500-599": 32, "600-700": 36, "701-780": 14
#     }

#     # Approximate spd
#     channel_outputs, output_spectrum, output_ppfd = light.approximate_spd(
#         channel_configs=channel_configs,
#         desired_distance_cm=distance,
#         desired_ppfd_umol_m2_s=ppfd,
#         desired_spectrum_nm_percent=spectrum,
#     )

#     print(channel_outputs)
#     assert output_ppfd == 1277.76

# # Set expected results
# expected_channel_outputs = {
#     "FR": 100.0, "CW1": 100.0, "CW2": 100.0, "CW3": 100.0, "CW4": 100.0, "WW": 100.0
# }
# expected_output_spectrum = {
#     "380-399": 0.0,
#     "400-499": 19.43,
#     "500-599": 39.5,
#     "600-700": 35.33,
#     "701-780": 5.74,
# }
# expected_output_ppfd = 548.52

# # Check results match expectations
# assert channel_outputs == expected_channel_outputs
# assert output_spectrum == expected_output_spectrum
# assert output_ppfd == expected_output_ppfd
