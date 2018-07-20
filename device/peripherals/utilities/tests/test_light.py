# Import standard python libraries
import sys, numpy

# Import module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.peripherals.utilities import light
except:
    # ... if running tests from same dir as light.py
    sys.path.append("../../../")
    from device.peripherals.utilities import light


channel_configs = [  # Config from taurus light panel
    {
        "name": {"brief": "FR", "verbose": "Far Red"},
        "channel": {"hardware": None, "software": 0},
        "spectrum_nm_percent": {
            "380-399": 0, "400-499": 0, "500-599": 0, "600-700": 12, "701-780": 88
        },
        "planar_distance_map": [
            {"distance_cm": 4, "ppfd_umol_m2_s": 34},
            {"distance_cm": 10, "ppfd_umol_m2_s": 16},
            {"distance_cm": 18, "ppfd_umol_m2_s": 8},
        ],
        "output_percent_map": [
            {"setpoint_percent": 0, "intensity_percent": 0},
            {"setpoint_percent": 25, "intensity_percent": 25},
            {"setpoint_percent": 50, "intensity_percent": 50},
            {"setpoint_percent": 75, "intensity_percent": 75},
            {"setpoint_percent": 100, "intensity_percent": 100},
        ],
    },
    {
        "name": {"brief": "R", "verbose": "Red"},
        "channel": {"hardware": None, "software": 2},
        "spectrum_nm_percent": {
            "380-399": 0, "400-499": 0, "500-599": 0, "600-700": 98, "701-780": 2
        },
        "planar_distance_map": [
            {"distance_cm": 4, "ppfd_umol_m2_s": 372},
            {"distance_cm": 10, "ppfd_umol_m2_s": 227},
            {"distance_cm": 18, "ppfd_umol_m2_s": 107},
        ],
        "output_percent_map": [
            {"setpoint_percent": 0, "intensity_percent": 0},
            {"setpoint_percent": 25, "intensity_percent": 25},
            {"setpoint_percent": 50, "intensity_percent": 50},
            {"setpoint_percent": 75, "intensity_percent": 75},
            {"setpoint_percent": 100, "intensity_percent": 100},
        ],
    },
    {
        "name": {"brief": "G", "verbose": "Green"},
        "channel": {"hardware": None, "software": 5},
        "spectrum_nm_percent": {
            "380-399": 0, "400-499": 10, "500-599": 89, "600-700": 1, "701-780": 0
        },
        "planar_distance_map": [
            {"distance_cm": 4, "ppfd_umol_m2_s": 130},
            {"distance_cm": 10, "ppfd_umol_m2_s": 70},
            {"distance_cm": 18, "ppfd_umol_m2_s": 35},
        ],
        "output_percent_map": [
            {"setpoint_percent": 0, "intensity_percent": 0},
            {"setpoint_percent": 25, "intensity_percent": 25},
            {"setpoint_percent": 50, "intensity_percent": 50},
            {"setpoint_percent": 75, "intensity_percent": 75},
            {"setpoint_percent": 100, "intensity_percent": 100},
        ],
    },
    {
        "name": {"brief": "B", "verbose": "Blue"},
        "channel": {"hardware": None, "software": 7},
        "spectrum_nm_percent": {
            "380-399": 0, "400-499": 99, "500-599": 1, "600-700": 0, "701-780": 0
        },
        "planar_distance_map": [
            {"distance_cm": 4, "ppfd_umol_m2_s": 261},
            {"distance_cm": 10, "ppfd_umol_m2_s": 200},
            {"distance_cm": 18, "ppfd_umol_m2_s": 116},
        ],
        "output_percent_map": [
            {"setpoint_percent": 0, "intensity_percent": 0},
            {"setpoint_percent": 25, "intensity_percent": 25},
            {"setpoint_percent": 50, "intensity_percent": 50},
            {"setpoint_percent": 75, "intensity_percent": 75},
            {"setpoint_percent": 100, "intensity_percent": 100},
        ],
    },
    {
        "name": {"brief": "CW", "verbose": "Cool White"},
        "channel": {"hardware": None, "software": 6},
        "spectrum_nm_percent": {
            "380-399": 0, "400-499": 23, "500-599": 47, "600-700": 27, "701-780": 3
        },
        "planar_distance_map": [
            {"distance_cm": 4, "ppfd_umol_m2_s": 234},
            {"distance_cm": 10, "ppfd_umol_m2_s": 178},
            {"distance_cm": 18, "ppfd_umol_m2_s": 104},
        ],
        "output_percent_map": [
            {"setpoint_percent": 0, "intensity_percent": 0},
            {"setpoint_percent": 25, "intensity_percent": 25},
            {"setpoint_percent": 50, "intensity_percent": 50},
            {"setpoint_percent": 75, "intensity_percent": 75},
            {"setpoint_percent": 100, "intensity_percent": 100},
        ],
    },
    {
        "name": {"brief": "WW", "verbose": "Warm White"},
        "channel": {"hardware": None, "software": 4},
        "spectrum_nm_percent": {
            "380-399": 0, "400-499": 8, "500-599": 38, "600-700": 49, "701-780": 5
        },
        "planar_distance_map": [
            {"distance_cm": 4, "ppfd_umol_m2_s": 504},
            {"distance_cm": 10, "ppfd_umol_m2_s": 198},
            {"distance_cm": 18, "ppfd_umol_m2_s": 96},
        ],
        "output_percent_map": [
            {"setpoint_percent": 0, "intensity_percent": 0},
            {"setpoint_percent": 25, "intensity_percent": 25},
            {"setpoint_percent": 50, "intensity_percent": 50},
            {"setpoint_percent": 75, "intensity_percent": 75},
            {"setpoint_percent": 100, "intensity_percent": 100},
        ],
    },
]

desired_distance_cm = 10
desired_ppfd_umol_m2_s = 800  # this is the measured ppfd @10cm with all lights on
desired_spectrum_nm_percent = {  # this is the measured spectrum @10cm with all channels on
    "380-399": 0, "400-499": 26, "500-599": 22, "600-700": 39, "701-780": 13
}


def test_calculate_desired_spd():
    desired_spd = light.calculate_desired_spd(
        ppfd_umol_m2_s=desired_ppfd_umol_m2_s,
        spectrum_nm_percent=desired_spectrum_nm_percent,
    )
    expected_spd = {
        "380-399": 0, "400-499": 208, "500-599": 176, "600-700": 312, "701-780": 104
    }
    assert desired_spd == expected_spd


def test_get_ppfd_at_distance_exact():
    ppfd = light.get_ppfd_at_distance(channel_config=channel_configs[0], distance=4)
    assert ppfd == 34
    ppfd = light.get_ppfd_at_distance(channel_config=channel_configs[0], distance=10)
    assert ppfd == 16
    ppfd = light.get_ppfd_at_distance(channel_config=channel_configs[0], distance=18)
    assert ppfd == 8


def test_get_ppfd_at_distance_inner_interpolate():
    ppfd = light.get_ppfd_at_distance(channel_config=channel_configs[0], distance=6)
    assert ppfd == 28
    ppfd = light.get_ppfd_at_distance(channel_config=channel_configs[0], distance=14)
    assert ppfd == 12


def test_get_ppfd_at_distance_outer_interpolate():
    ppfd = light.get_ppfd_at_distance(channel_config=channel_configs[0], distance=3)
    assert ppfd == 34
    ppfd = light.get_ppfd_at_distance(channel_config=channel_configs[0], distance=19)
    assert ppfd == 8


def test_discretize_spd():
    spd = {"380-399": 0, "400-499": 208, "500-599": 176, "600-700": 312, "701-780": 104}
    dspd = light.discretize_spd(spd)

    # Round all values to 2 decimals
    for key in dspd.keys():
        dspd[key] = round(dspd[key], 2)

    # Check min, middle, max values for each band
    assert (dspd[380], dspd[390], dspd[399]) == (0, 0, 0)
    assert (dspd[400], dspd[450], dspd[499]) == (2.08, 2.08, 2.08)
    assert (dspd[500], dspd[550], dspd[599]) == (1.76, 1.76, 1.76)
    assert (dspd[600], dspd[650], dspd[700]) == (3.09, 3.09, 3.09)
    assert (dspd[701], dspd[750], dspd[780]) == (1.3, 1.3, 1.3)


def translate_spd():
    from_spd = {"300-399": 50, "400-499": 50}
    to_spd = {"300-349": 0, "350-399": 0, "400-449": 0, "450-499": 0}
    translated_spd = light.translage_spd(from_spd, to_spd)
    expected_spd = {"300-349": 25, "350-399": 25, "400-449": 25, "450-499": 25}
    assert translated_spd == expected_spd


def test_build_channel_spd_matrix():
    desired_spd = {
        "380-399": 0, "400-499": 208, "500-599": 176, "600-700": 312, "701-780": 104
    }

    channel_spd_matrix = light.build_channel_spd_matrix(
        channel_configs=channel_configs,
        distance=desired_distance_cm,
        reference_spd=desired_spd,
    )

    # Calculated by multiplying spectral percent * ppfd@distance
    fr = [0, 0, 0, 1.92, 14.08]
    r = [0, 0, 0, 222.46, 4.54]
    g = [0, 7, 62.3, 0.7, 0]
    b = [0, 198, 2, 0, 0]
    cw = [0, 40.94, 83.66, 48.06, 5.34]
    ww = [0, 15.84, 75.24, 97.02, 9.9]
    matrix = numpy.array([fr, r, g, b, cw, ww])
    expected_spd_matrix = numpy.transpose(matrix)

    # Check expexted matches output
    assert channel_spd_matrix.tolist() == expected_spd_matrix.tolist()


def test_build_desired_spd_vector():
    desired_spd_vector = light.build_desired_spd_vector(
        desired_spectrum_nm_percent=desired_spectrum_nm_percent,
        desired_ppfd_umol_m2_s=desired_ppfd_umol_m2_s,
    )
    assert desired_spd_vector.tolist() == [0, 208, 176, 312, 104]


def test_calculate_channel_output_vector():
    desired_spd_vector = light.build_desired_spd_vector(
        desired_spectrum_nm_percent=desired_spectrum_nm_percent,
        desired_ppfd_umol_m2_s=desired_ppfd_umol_m2_s,
    )
    desired_spd = {
        "380-399": 0, "400-499": 208, "500-599": 176, "600-700": 312, "701-780": 104
    }
    channel_spd_matrix = light.build_channel_spd_matrix(
        channel_configs=channel_configs,
        distance=desired_distance_cm,
        reference_spd=desired_spd,
    )
    channel_outputs = light.calculate_channel_output_vector(
        channel_spd_matrix=channel_spd_matrix, desired_spd_vector=desired_spd_vector
    )
    print("channel_outputs = {}".format(channel_outputs))

    assert channel_outputs == [1, 0.75, 0.25, 0.75, 1, 1]


# channel_output_intensities_dict = light.dictify_channel_output_vector(
#     channel_configs=channel_configs,
#     channel_output_vector=channel_output_intensities_vector,
# )
# assert channel_output_intensities_dict == {"FR": 46.0, "WW": 54.0}

# channel_output_setpoints_dict = light.convert_channel_output_intensities(
#     channel_configs=channel_configs,
#     output_intensities=channel_output_intensities_dict,
# )
# assert channel_output_setpoints_dict == {"FR": 34.85, "WW": 40.91}

# output_spd_vector = light.calculate_output_spd(
#     channel_spd_matrix=channel_spd_matrix,
#     channel_output_vector=channel_output_intensities_vector,
# )
# assert output_spd_vector == [10.0, 10.0, 34.6, 6.92, 10.0, 10.0]

# output_spd_dict = light.dictify_vector(
#     vector=output_spd_vector, reference_dict=desired_spd
# )
# assert (
#     output_spd_dict
#     == {
#         "400-449": 10.0,
#         "449-499": 10.0,
#         "500-549": 34.6,
#         "550-559": 6.92,
#         "600-649": 10.0,
#         "650-699": 10.0,
#     }
# )

# output_spectrum_vector, output_ppfd_umol_m2_s = light.deconstruct_spd_vector(
#     spd_vector=output_spd_vector
# )
# assert output_spectrum_vector == [12.27, 12.27, 42.44, 8.49, 12.27, 12.27]
# assert output_ppfd_umol_m2_s == 81.52

# output_spectrum_dict = light.dictify_vector(
#     vector=output_spectrum_vector, reference_dict=desired_spd
# )
# assert (
#     output_spectrum_dict
#     == {
#         "400-449": 12.27,
#         "449-499": 12.27,
#         "500-549": 42.44,
#         "550-559": 8.49,
#         "600-649": 12.27,
#         "650-699": 12.27,
#     }
# )


# def test_approximate_spd():
#     channel_output_setpoints, output_spectrum_nm_percent, output_ppfd_umol_m2_s = light.approximate_spd(
#         channel_configs=channel_configs,
#         desired_distance_cm=desired_distance_cm,
#         desired_ppfd_umol_m2_s=desired_ppfd_umol_m2_s,
#         desired_spectrum_nm_percent=desired_spectrum_nm_percent,
#     )
#     assert channel_output_setpoints == {"FR": 34.85, "WW": 40.91}
#     assert (
#         output_spectrum_nm_percent
#         == {
#             "400-449": 12.27,
#             "449-499": 12.27,
#             "500-549": 42.44,
#             "550-559": 8.49,
#             "600-649": 12.27,
#             "650-699": 12.27,
#         }
#     )
#     assert output_ppfd_umol_m2_s == 81.52


# def tests_calculate_resultant_spd():

#     desired_spd = light.calculate_desired_spd(
#         ppfd_umol_m2_s=desired_ppfd_umol_m2_s,
#         spectrum_nm_percent=desired_spectrum_nm_percent,
#     )

#     output_spectrum_nm_percent, output_ppfd_umol_m2_s = light.calculate_resultant_spd(
#         channel_configs=channel_configs,
#         reference_spd=desired_spd,
#         channel_output_setpoints={"FR": 34.85, "WW": 40.91},
#         distance=desired_distance_cm,
#     )
#     assert (
#         output_spectrum_nm_percent
#         == {
#             "400-449": 12.27,
#             "449-499": 12.27,
#             "500-549": 42.44,
#             "550-559": 8.49,
#             "600-649": 12.27,
#             "650-699": 12.27,
#         }
#     )
#     assert output_ppfd_umol_m2_s == 81.52
