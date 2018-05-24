# Import standard python modules
import numpy

# Import device utilities
from device.utilities import math


def calculate_desired_spd(intensity_watts, spectrum_nm_percent):
    """ Calculates desired spd. """
    for wavelength_band, percent in spectrum_nm_percent.items():
        spectrum_nm_percent[wavelength_band] = intensity_watts * percent / 100
    return spectrum_nm_percent


def get_intensity_at_distance(channel_config, distance):
    """ Gets intensity (watts) at illumination distance (cm). """
    planar_distance_map = channel_config["planar_distance_map"]
    distance_list = []
    intensity_list = []
    for entry in planar_distance_map:
        distance_list.append(entry["distance_cm"])
        intensity_list.append(entry["intensity_watts"])
    intensity = math.interpolate(distance_list, intensity_list, distance)
    return intensity


def discretize_spd(spd):
    """ Discretizes channel spd. Converts values banded by wavelengths greater
        than 1 nm into a set of wavelengths at 1nm granularity with corresponding
        value. """
    discretized_spd = {}
    for wavelength_band, intensity in spd.items():
        minimum, maximum = list(map(int, wavelength_band.split("-")))
        discretized_spd.update(math.discretize(minimum, maximum, intensity))
    return discretized_spd


def translate_spd(from_spd, to_spd):
    """ Translates a channels spectral power distribution ranges to match 
    the desired SPD ranges. """

    # Get wavelength bands from desired spd
    wavelength_bands = []
    for wavelength_band, percent in to_spd.items():
        wavelength_bands.append(wavelength_band)

    # Build translated channel spd shell with same wavelength bands as desired spd 
    translated_channel_spd = {}
    for wavelength_band in wavelength_bands:
        translated_channel_spd[wavelength_band] = 0

    # Discretize channel spd
    discretized_channel_spd = discretize_spd(from_spd)

    # Re-distribute discretized channel spd into translated spd w/new bands
    for wavelength, intensity in discretized_channel_spd.items():
        for wavelength_band, _ in translated_channel_spd.items():
            minimum, maximum = list(map(int, wavelength_band.split("-")))
            if wavelength in range(minimum, maximum + 1):
                translated_channel_spd[wavelength_band] += intensity
                break;

    # Round output intensity
    for wavelength_band, intensity in translated_channel_spd.items():
        translated_channel_spd[wavelength_band] = round(intensity, 3)

    # Return translated spd
    return translated_channel_spd



def build_channel_spd_matrix(channel_configs, distance, desired_spd):
    """ Builds channel spectral power distribution matrix. """

    channel_spd_matrix = []
    for channel_config in channel_configs:

        # Get channel intensity and spd
        intensity_watts = get_intensity_at_distance(channel_config, distance)
        channel_spd = channel_config["spectrum_nm_percent"]

        # Scale channel spd to intensity at distance
        scaled_channel_spd = {}
        for wavelength_band, intensity_percent in channel_spd.items():
            scaled_channel_spd[wavelength_band] = intensity_watts * intensity_percent / 100

        # Translate channel spd to match wavelength bands of desired spd
        translated_channel_spd = translate_spd(
            from_spd = scaled_channel_spd,
            to_spd = desired_spd,
        )

        # Build channel spd vector and append to matrix
        channel_spd_vector = []
        for _, intensity in translated_channel_spd.items():
            channel_spd_vector.append(intensity)
        channel_spd_matrix.append(channel_spd_vector)

    # Convert to properly dimensioned numpy array and return
    channel_spd_matrix = numpy.array(channel_spd_matrix)
    channel_spd_matrix = numpy.transpose(channel_spd_matrix)
    return channel_spd_matrix


def build_desired_spd_vector(desired_spectrum_nm_percent, desired_intensity_watts):
    """ Builds desired spd vector. """
    desired_spd_vector = []
    for band, percent in desired_spectrum_nm_percent.items():
        desired_spd_vector.append(desired_intensity_watts * percent / 100)
    desired_spd_vector = numpy.array(desired_spd_vector)
    return desired_spd_vector


def calculate_channel_output_vector(channel_spd_matrix, desired_spd_vector):
    """ Generates channel output percents to approximate desired
        spectral power distribution. """

    # Calculate weighted channel outputs
    weighted_channel_outputs = math.nnls(channel_spd_matrix, desired_spd_vector)

    # Scale channel outputs
    max_output = max(weighted_channel_outputs)
    if max_output > 1:
        scaled_channel_outputs = weighted_channel_outputs / max_output
    else:
        scaled_channel_outputs = weighted_channel_outputs

    # Create channel output vector
    channel_output_vector = []
    for scaled_channel_output in scaled_channel_outputs:
        channel_output_vector.append(round(scaled_channel_output, 2))

    # Return channel output vector
    return channel_output_vector


def calculate_output_spd(channel_spd_matrix, channel_output_vector):
    """ Calculates ouput spectral power distribution. """
    raw_output_spd = channel_spd_matrix.dot(channel_output_vector)
    output_spd = []
    for element in raw_output_spd:
        output_spd.append(round(element, 3))
    return output_spd


def dictify_channel_output_vector(channel_configs, channel_output_vector):
    """ Convert channel output vector into its dictionary representation. """
    channel_output_dict = {}
    for index, channel_config in enumerate(channel_configs):
        name = channel_config["name"]["brief"]
        channel_output_dict[name] = channel_output_vector[index]
    return channel_output_dict


def deconstruct_spd_vector(spd_vector, decimals):
	""" Deconstructs vector, returns normalized vector with intensity. """
	intensity = sum(spd_vector)
	new_spd_vector = []
	for element in spd_vector:
		new_spd_vector.append(round(float(element) / intensity * 100, decimals))
	return new_spd_vector, round(intensity, decimals)


def dictify_vector(vector, reference_dict):
    """ Converts output spd vector into its dictionary representation. """
    dict_ = {}
    index = 0
    for key, _ in reference_dict.items():
        dict_[key] = vector[index]
        index += 1
    return dict_


def approximate_spd(channel_configs, desired_distance_cm, 
	desired_intensity_watts, desired_spectrum_nm_percent):
    """ Approximates spectral power distribution. """

    desired_spd = calculate_desired_spd(
        intensity_watts = desired_intensity_watts,
        spectrum_nm_percent = desired_spectrum_nm_percent
    )

    channel_spd_matrix = build_channel_spd_matrix(
        channel_configs = channel_configs,
        distance = desired_distance_cm,
        desired_spd = desired_spd,
    )

    desired_spd_vector = build_desired_spd_vector(
        desired_spectrum_nm_percent = desired_spectrum_nm_percent, 
        desired_intensity_watts = desired_intensity_watts,
    )

    channel_output_vector = calculate_channel_output_vector(
        channel_spd_matrix = channel_spd_matrix, 
        desired_spd_vector = desired_spd_vector,
    )

    channel_output_dict = dictify_channel_output_vector(
        channel_configs = channel_configs,
        channel_output_vector = channel_output_vector,
    )

    output_spd_vector = calculate_output_spd(
        channel_spd_matrix = channel_spd_matrix,
        channel_output_vector = channel_output_vector, 
    )

    output_spectrum_vector, output_intensity_watts = deconstruct_spd_vector(
        spd_vector = output_spd_vector,
        decimals = 2,
    )

    output_spectrum_dict = dictify_vector(
        vector = output_spectrum_vector,
        reference_dict = desired_spd,
    )

    return channel_output_dict, output_spectrum_dict, output_intensity_watts