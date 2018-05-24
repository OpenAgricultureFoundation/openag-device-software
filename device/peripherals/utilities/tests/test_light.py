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


def test_individual():
	desired_spd = light.calculate_desired_spd(
	    intensity_watts = desired_intensity_watts,
	    spectrum_nm_percent = desired_spectrum_nm_percent
	)
	assert desired_spd == {'400-449': 10, '449-499': 10, '500-549': 30, '550-559': 30, '600-649': 10, '650-699': 10}


	channel_spd_matrix = light.build_channel_spd_matrix(
	    channel_configs = channel_configs,
	    distance = desired_distance_cm,
	    desired_spd = desired_spd,
	)
	assert channel_spd_matrix.tolist() == [[10.0, 10.0], [10.0, 10.0], [40.0, 30.0], [8.0, 6.0], [10.0, 10.0], [10.0, 10.0]]

	desired_spd_vector = light.build_desired_spd_vector(
	    desired_spectrum_nm_percent = desired_spectrum_nm_percent, 
	    desired_intensity_watts = desired_intensity_watts,
	)
	assert desired_spd_vector.tolist() == [10.0, 10.0, 30.0, 30.0, 10.0, 10.0]

	channel_output_vector = light.calculate_channel_output_vector(
	    channel_spd_matrix = channel_spd_matrix, 
	    desired_spd_vector = desired_spd_vector,
	)
	assert channel_output_vector == [0.46, 0.54]

	channel_output_dict = light.dictify_channel_output_vector(
	    channel_configs = channel_configs,
	    channel_output_vector = channel_output_vector,
	)
	assert channel_output_dict == {'FR': 0.46, 'WW': 0.54}

	output_spd_vector = light.calculate_output_spd(
	    channel_spd_matrix = channel_spd_matrix,
	    channel_output_vector = channel_output_vector, 
	)
	assert output_spd_vector ==[10.0, 10.0, 34.6, 6.92, 10.0, 10.0]

	output_spd_dict = light.dictify_vector(
		vector = output_spd_vector,
	    reference_dict = desired_spd,
	)
	assert output_spd_dict == {'400-449': 10.0, '449-499': 10.0, '500-549': 34.6, '550-559': 6.92, '600-649': 10.0, '650-699': 10.0}

	output_spectrum_vector, output_intensity_watts = light.deconstruct_spd_vector(
		spd_vector = output_spd_vector,
		decimals = 2,
	)
	assert output_spectrum_vector == [12.27, 12.27, 42.44, 8.49, 12.27, 12.27]
	assert output_intensity_watts == 81.52

	output_spectrum_dict = light.dictify_vector(
		vector = output_spectrum_vector,
	    reference_dict = desired_spd,
	)
	assert output_spectrum_dict == {'400-449': 12.27, '449-499': 12.27, '500-549': 42.44, '550-559': 8.49, '600-649': 12.27, '650-699': 12.27}


def test_integration():
	channel_outputs, output_spectrum_nm_percent, output_intensity_watts = light.approximate_spd(
		channel_configs = channel_configs, 
		desired_distance_cm = desired_distance_cm, 
		desired_intensity_watts = desired_intensity_watts, 
		desired_spectrum_nm_percent = desired_spectrum_nm_percent,
	)
	assert channel_outputs == {'FR': 0.46, 'WW': 0.54}
	assert output_spectrum_nm_percent == {'400-449': 12.27, '449-499': 12.27, '500-549': 42.44, '550-559': 8.49, '600-649': 12.27, '650-699': 12.27}
	assert output_intensity_watts == 81.52