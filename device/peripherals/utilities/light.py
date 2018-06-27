# Import standard python modules
import numpy

# Import device utilities
from device.utilities import maths

# TODO: Verify spectrums sum to 100%


def calculate_desired_spd(intensity_watts, spectrum_nm_percent):
    """ Calculates desired spd. """
    for wavelength_band, percent in spectrum_nm_percent.items():
        spectrum_nm_percent[wavelength_band] = intensity_watts * percent / 100.0
    return spectrum_nm_percent


def get_intensity_at_distance(channel_config, distance):
    """ Gets intensity (watts) at illumination distance (cm). """
    planar_distance_map = channel_config["planar_distance_map"]
    distance_list = []
    intensity_list = []
    for entry in planar_distance_map:
        distance_list.append(entry["distance_cm"])
        intensity_list.append(entry["intensity_watts"])
    intensity = maths.interpolate(distance_list, intensity_list, distance)
    return intensity


def discretize_spd(spd):
    """ Discretizes channel spd. Converts values banded by wavelengths greater
        than 1 nm into a set of wavelengths at 1nm granularity with corresponding
        value. """
    discretized_spd = {}
    for wavelength_band, intensity in spd.items():
        minimum, maximum = list(map(int, wavelength_band.split("-")))
        discretized_spd.update(maths.discretize(minimum, maximum, intensity))
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
                break

    # Round output intensity
    for wavelength_band, intensity in translated_channel_spd.items():
        rounded_intensity = float("{:.3f}".format(intensity))
        translated_channel_spd[wavelength_band] = rounded_intensity

    # Return translated spd
    return translated_channel_spd


def build_channel_spd_matrix(channel_configs, distance, reference_spd):
    """ Builds channel spectral power distribution matrix from channel configs
        at distance with spectral bands that match the reference spd. """

    channel_spd_matrix = []
    for channel_config in channel_configs:

        # Get channel intensity and spd
        intensity_watts = get_intensity_at_distance(channel_config, distance)
        channel_spd = channel_config["spectrum_nm_percent"]

        # Scale channel spd to intensity at distance
        scaled_channel_spd = {}
        for wavelength_band, intensity_percent in channel_spd.items():
            scaled_channel_spd[wavelength_band] = (
                intensity_watts * intensity_percent / 100
            )

        # Translate channel spd to match wavelength bands of desired spd
        translated_channel_spd = translate_spd(
            from_spd=scaled_channel_spd, to_spd=reference_spd
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
    weighted_channel_outputs = maths.nnls(channel_spd_matrix, desired_spd_vector)

    # Scale channel outputs
    max_output = max(weighted_channel_outputs)
    if max_output > 1:
        scaled_channel_outputs = weighted_channel_outputs / max_output
    else:
        scaled_channel_outputs = weighted_channel_outputs

    # Create channel output vector
    channel_output_vector = []
    for scaled_channel_output in scaled_channel_outputs:
        rounded_channel_output = float("{:.2f}".format(scaled_channel_output))
        channel_output_vector.append(rounded_channel_output)

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
        channel_output_dict[name] = channel_output_vector[index] * 100.0
    return channel_output_dict


def convert_channel_output_intensity(output_percent_map, output_intensity):
    """ Converts output setpoint to output intensity from 
        provided output percent map. """
    intensity_list = []
    setpoint_list = []
    for entry in output_percent_map:
        intensity_list.append(entry["intensity_percent"])
        setpoint_list.append(entry["setpoint_percent"])
    output_setpoint = maths.interpolate(intensity_list, setpoint_list, output_intensity)
    rounded_output_setpoint = float("{:.2f}".format(output_setpoint))
    return rounded_output_setpoint


def convert_channel_output_intensities(channel_configs, output_intensities):
    """ Converts channel output setpoints to channel output intensites from 
        provided channel configs. """
    output_setpoints = {}
    for channel_name, output_intensity in output_intensities.items():
        for channel_config in channel_configs:
            name = channel_config["name"]["brief"]
            if channel_name == name:
                output_percent_map = channel_config["output_percent_map"]
                output_setpoint = convert_channel_output_intensity(
                    output_percent_map=output_percent_map,
                    output_intensity=output_intensity,
                )
                output_setpoints[channel_name] = output_setpoint
                break
    return output_setpoints


def convert_channel_output_setpoint(output_percent_map, output_setpoint):
    """ Converts output setpoint to output intensity from 
        provided output percent map. """
    intensity_list = []
    setpoint_list = []
    for entry in output_percent_map:
        intensity_list.append(entry["intensity_percent"])
        setpoint_list.append(entry["setpoint_percent"])
    output_intensity = maths.interpolate(setpoint_list, intensity_list, output_setpoint)
    rounded_output_intensity = float("{:.2f}".format(output_intensity))
    return rounded_output_intensity


def convert_channel_output_setpoints(channel_configs, output_setpoints):
    """ Converts channel output setpoints to channel output intensites from 
        provided channel configs. """
    output_intensities = {}
    for channel_name, output_setpoint in output_setpoints.items():
        for channel_config in channel_configs:
            name = channel_config["name"]["brief"]
            if channel_name == name:
                output_percent_map = channel_config["output_percent_map"]
                output_intensity = convert_channel_output_setpoint(
                    output_percent_map=output_percent_map,
                    output_setpoint=output_setpoint,
                )
                output_intensities[channel_name] = output_intensity
                break
    return output_intensities


def deconstruct_spd_vector(spd_vector):
    """ Deconstructs vector, returns normalized vector with intensity. """
    intensity = sum(spd_vector)
    rounded_intensity = float("{:.2f}".format(intensity))
    new_spd_vector = []
    for element in spd_vector:
        if intensity != 0:
            value = float(element) / intensity * 100.0
        else:
            value = 0
        rounded_value = float("{:.2f}".format(value))
        new_spd_vector.append(rounded_value)

    return new_spd_vector, rounded_intensity


def dictify_vector(vector, reference_dict):
    """ Converts vector into dictionary representation with keys from reference dict. """
    dict_ = {}
    index = 0
    for key, _ in reference_dict.items():
        dict_[key] = vector[index]
        index += 1
    return dict_


def vectorize_dict(dict_):
    """ Converts dict into vector representation. """
    list_ = []
    for _, value in dict_.items():
        list_.append(value / 100.0)
    vector = numpy.array(list_)
    return vector


def approximate_spd(
    channel_configs,
    desired_distance_cm,
    desired_intensity_watts,
    desired_spectrum_nm_percent,
):
    """ Approximates spectral power distribution. """

    desired_spd = calculate_desired_spd(
        intensity_watts=desired_intensity_watts,
        spectrum_nm_percent=desired_spectrum_nm_percent,
    )

    channel_spd_matrix = build_channel_spd_matrix(
        channel_configs=channel_configs,
        distance=desired_distance_cm,
        reference_spd=desired_spd,
    )

    desired_spd_vector = build_desired_spd_vector(
        desired_spectrum_nm_percent=desired_spectrum_nm_percent,
        desired_intensity_watts=desired_intensity_watts,
    )

    channel_output_intensities_vector = calculate_channel_output_vector(
        channel_spd_matrix=channel_spd_matrix, desired_spd_vector=desired_spd_vector
    )

    channel_output_intensities_dict = dictify_channel_output_vector(
        channel_configs=channel_configs,
        channel_output_vector=channel_output_intensities_vector,
    )

    channel_output_setpoints_dict = convert_channel_output_intensities(
        channel_configs=channel_configs,
        output_intensities=channel_output_intensities_dict,
    )

    output_spd_vector = calculate_output_spd(
        channel_spd_matrix=channel_spd_matrix,
        channel_output_vector=channel_output_intensities_vector,
    )

    output_spectrum_vector, output_intensity_watts = deconstruct_spd_vector(
        spd_vector=output_spd_vector
    )

    output_spectrum_dict = dictify_vector(
        vector=output_spectrum_vector, reference_dict=desired_spd
    )

    return channel_output_setpoints_dict, output_spectrum_dict, output_intensity_watts


def calculate_resultant_spd(
    channel_configs, reference_spd, channel_output_setpoints, distance
):
    """ Generates spd from provided channel outputs at distance. Returns 
        spd with the same spectral bands as the reference spd. """

    channel_spd_matrix = build_channel_spd_matrix(
        channel_configs=channel_configs, distance=distance, reference_spd=reference_spd
    )

    channel_output_intensities = convert_channel_output_setpoints(
        channel_configs=channel_configs, output_setpoints=channel_output_setpoints
    )

    channel_output_vector = vectorize_dict(dict_=channel_output_intensities)

    output_spd_vector = calculate_output_spd(
        channel_spd_matrix=channel_spd_matrix,
        channel_output_vector=channel_output_vector,
    )

    output_spectrum_vector, output_intensity_watts = deconstruct_spd_vector(
        spd_vector=output_spd_vector
    )

    output_spectrum_dict = dictify_vector(
        vector=output_spectrum_vector, reference_dict=reference_spd
    )

    return output_spectrum_dict, output_intensity_watts
