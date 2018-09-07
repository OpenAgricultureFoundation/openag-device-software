# Import standard python modules
import numpy

# Import python types
from typing import Dict, Any, List, Tuple

# Import device utilities
from device.utilities import maths
from device.utilities import accessors


def approximate_spd(
    channel_properties: Dict[str, Any],
    des_distance: float,
    des_intensity: float,
    des_spectrum: Dict[str, float],
):
    """Approximates spectral power distribution."""

    # Get desired spd vector (i.e. `b` in Ax=b)
    desired_spd_dict = calculate_spd_dict(des_intensity, des_spectrum)
    desired_spd_vector = accessors.vectorize_dict(desired_spd_dict)
    print("b = {}".format(desired_spd_vector))

    # Get channel spd matrix (i.e. `A` in Ax=b)
    raw_channel_spd_ndict = build_channel_spd_ndict(channel_properties, des_distance)
    channel_spd_ndict = translate_spd_ndict(raw_channel_spd_ndict, desired_spd_dict)
    channel_spd_matrix = accessors.matrixify_nested_dict(channel_spd_ndict)
    print("A = {}".format(channel_spd_matrix))

    # Get channel logic vector (i.e `x` in Ax=b) with bounded non-negative least-squares approximation
    channel_logic_vector = maths.bnnls(channel_spd_matrix, desired_spd_vector)
    print("x = {}".format(channel_logic_vector))

    # channel_output_intensities_vector = calculate_channel_output_vector(
    #     channel_spd_matrix=channel_spd_matrix,
    #     desired_spd_dict_vector=desired_spd_dict_vector,
    # )

    # channel_output_intensities_dict = dictify_channel_output_vector(
    #     channel_properties=channel_properties,
    #     channel_output_vector=channel_output_intensities_vector,
    # )

    # channel_output_setpoints_dict = convert_channel_output_intensities(
    #     channel_properties=channel_properties,
    #     output_intensities=channel_output_intensities_dict,
    # )

    # output_spd_vector = calculate_output_spd(
    #     channel_spd_matrix=channel_spd_matrix,
    #     channel_output_vector=channel_output_intensities_vector,
    # )

    # output_spectrum_vector, output_intensity = deconstruct_spd_vector(
    #     spd_vector=output_spd_vector
    # )

    # output_spectrum_dict = dictify_vector(
    #     vector=output_spectrum_vector, reference_dict=desired_spd_dict
    # )

    # return channel_output_setpoints_dict, output_spectrum_dict, output_intensity


def calculate_spd_dict(intensity: float, spectrum: Dict[str, float]):
    """Calculates spd dict from intensity and spectrum."""
    spd_dict = {}
    for wavelength_band, percent in spectrum.items():
        spd_dict[wavelength_band] = intensity * percent / 100.0
    return spd_dict


def build_channel_spd_ndict(
    channel_properties: Dict[str, Any], distance: float
) -> Dict[str, Dict[str, float]]:
    """Builds channel spd nested dict."""

    # Initialize channel property variables
    channels = channel_properties.get("channels", {})
    channel_types = channel_properties.get("channel_types", {})
    intensity_map = channel_properties.get("intensity_map_cm_umol", 0)

    # Get channel weights
    channel_weights = {}
    for channel_key, channel_dict in channels.items():
        channel_type = channel_dict.get("type")
        if channel_type in channel_weights:
            channel_weights[channel_type] += 1
        else:
            channel_weights[channel_type] = 1

    # Get cumulative intensity at distance
    cumulative_intensity = get_intensity_at_distance(intensity_map, distance)

    # Build channel spd dict
    channel_spd_ndict = {}
    for channel_key, channel_weight in channel_weights.items():

        # Get channel intensity
        channel_type = channel_types.get(channel_key, {})
        channel_relative_intensity = channel_type.get("relative_intensity_percent", 0)
        channel_intensity = cumulative_intensity * channel_relative_intensity / 100.0

        # Get channel spectrum
        channel_spectrum = channel_type.get("spectrum_nm_percent", {})

        # Get channel spd
        channel_spd_dict = {}
        for spectral_band, band_relative_intensity in channel_spectrum.items():
            band_intensity = channel_intensity * band_relative_intensity / 100
            weighted_band_intensity = band_intensity * channel_weight
            channel_spd_dict[spectral_band] = weighted_band_intensity

        # Add channel spd to channel spd dict
        channel_spd_ndict[channel_key] = channel_spd_dict

    # Successfully built channel spd nested dict
    return channel_spd_ndict


def get_intensity_at_distance(
    intensity_map: Dict[str, float], distance: float
) -> float:
    """Interpolates intensity from intensity map at illumination distance."""
    distance_list = []
    intensity_list = []
    for distance_, intensity in intensity_map.items():
        distance_list.append(float(distance_))
        intensity_list.append(intensity)
    return maths.interpolate(distance_list, intensity_list, distance)


def translate_spd_ndict(
    spd_ndict: Dict[str, float], reference_spd_dict: Dict[str, float]
) -> Dict[str, float]:
    """Translates a spd nested dict to match wavelength bands of reference spd dict."""
    translated_spd_ndict = {}
    for key, spd_dict in spd_ndict.items():
        translated_spd_dict = translate_spd_dict(spd_dict, reference_spd_dict)
        translated_spd_ndict[key] = translated_spd_dict
    return translated_spd_ndict


def translate_spd_dict(
    spd_dict: Dict[str, float], reference_spd_dict: Dict[str, float]
) -> Dict[str, float]:
    """Translates spd dict ranges to match reference spd dict ranges."""

    # Get wavelength bands from reference spd dict
    wavelength_bands = []
    for wavelength_band, percent in reference_spd_dict.items():
        wavelength_bands.append(wavelength_band)

    # Build translated spd dict shell with same wavelength bands as reference spd dict
    translated_spd_dict = {}
    for wavelength_band in wavelength_bands:
        translated_spd_dict[wavelength_band] = 0

    # Discretize spd dict
    discretized_spd_dict = discretize_spd_dict(spd_dict)

    # Re-distribute discretized spd dict into translated spd dict w/new bands
    for wavelength, intensity in discretized_spd_dict.items():
        for wavelength_band, _ in translated_spd_dict.items():
            minimum, maximum = list(map(int, wavelength_band.split("-")))
            if wavelength in range(minimum, maximum + 1):
                translated_spd_dict[wavelength_band] += intensity
                break

    # Round output intensity
    for wavelength_band, intensity in translated_spd_dict.items():
        rounded_intensity = float("{:.3f}".format(intensity))
        translated_spd_dict[wavelength_band] = rounded_intensity

    # Return translated spd
    return translated_spd_dict


def discretize_spd_dict(spd_dict: Dict[str, float]) -> Dict[str, float]:
    """Discretizes an spd dict. Converts values banded by wavelengths greater
    than 1 nm into a set of wavelengths at 1nm granularity with corresponding
    value. Applies no weighting based on wavelength, but should (E=hf)."""
    discretized_spd_dict = {}
    for wavelength_band, intensity in spd_dict.items():
        minimum, maximum = list(map(int, wavelength_band.split("-")))
        discretized_spd_dict.update(maths.discretize(minimum, maximum, intensity))
    return discretized_spd_dict


# def solve_channel_logic_vector(
#     channel_spd_matrix: numpy.ndarray, desired_spd_vector: numpy.ndarray
# ) -> numpy.ndarray:
#     """Solves for channel logic vector."""

#     # Use bounded non-negative least squares approximation
#     channel_logic_vector = maths.bnnls(channel_spd_matrix, desired_spd_vector)

#     # Create channel output vector
#     channel_output_vector = []
#     for channel_output in channel_outputs:
#         channel_output_vector.append(round(channel_output, 2))

#     # Return channel output vector
#     return channel_output_vector


def calculate_output_spd(channel_spd_matrix, channel_output_vector):
    """ Calculates ouput spectral power distribution. """
    raw_output_spd = channel_spd_matrix.dot(channel_output_vector)
    output_spd = []
    for element in raw_output_spd:
        output_spd.append(round(element, 3))
    return output_spd


def dictify_channel_output_vector(channel_properties, channel_output_vector):
    """ Convert channel output vector into its dictionary representation. """
    channel_output_dict = {}
    for index, channel_config in enumerate(channel_properties):
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


def convert_channel_output_intensities(channel_properties, output_intensities):
    """ Converts channel output setpoints to channel output intensites from 
        provided channel configs. """
    output_setpoints = {}
    for channel_name, output_intensity in output_intensities.items():
        for channel_config in channel_properties:
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


def convert_channel_output_setpoints(channel_properties, output_setpoints):
    """ Converts channel output setpoints to channel output intensites from 
        provided channel configs. """
    output_intensities = {}
    for channel_name, output_setpoint in output_setpoints.items():
        for channel_config in channel_properties:
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


def calculate_resultant_spd(
    channel_properties, reference_spd, channel_output_setpoints, distance
):
    """ Generates spd from provided channel outputs at distance. Returns 
        spd with the same spectral bands as the reference spd. """

    channel_spd_matrix = build_channel_spd_matrix(
        channel_properties=channel_properties,
        distance=distance,
        reference_spd=reference_spd,
    )

    channel_output_intensities = convert_channel_output_setpoints(
        channel_properties=channel_properties, output_setpoints=channel_output_setpoints
    )

    channel_output_vector = vectorize_dict(dict_=channel_output_intensities)

    output_spd_vector = calculate_output_spd(
        channel_spd_matrix=channel_spd_matrix,
        channel_output_vector=channel_output_vector,
    )

    output_spectrum_vector, output_intensity = deconstruct_spd_vector(
        spd_vector=output_spd_vector
    )

    output_spectrum_dict = dictify_vector(
        vector=output_spectrum_vector, reference_dict=reference_spd
    )

    return output_spectrum_dict, output_intensity


def calculate_ulrf_from_percents(
    channel_properties: Dict[str, str],
    channel_power_percents: Dict[str, float],
    distance: float,
) -> Tuple[Dict, float, float]:
    """Calculates universal light recipe format (ULRF) for provided channel 
    configuration, channel power percents, and illumination distance."""

    # Get min/max distance for channels
    # TODO: Verify code is being checked to ensure planar distance map is ordered list
    min_distance = channel_properties[0]["planar_distance_map"][0]["distance"]
    max_distance = channel_properties[-1]["planar_distance_map"][0]["distance"]

    # Check distance in range, else use extrema
    if distance > max_distance:
        distance = max_distance
    if distance < min_distance:
        distance = min_distance

    # Get reference SPD from channel configs
    reference_spd = channel_properties[0]["spectrum"]

    # Calculate resultant spectrum and intensity from channel power percents
    spectrum, intensity = calculate_resultant_spd(
        channel_properties=channel_properties,
        reference_spd=reference_spd,
        channel_output_setpoints=channel_power_percents,
        distance=distance,
    )

    return spectrum, intensity, distance


def calculate_ulrf_from_watts(
    channel_properties: Dict[str, str],
    channel_power_watts: Dict[str, float],
    distance: float,
) -> Tuple[Dict, float, float]:
    """Calculates universal light recipe format (ULRF) for provided channel 
    configuration, channel power watts, and illumination distance."""
    raise NotImplementedError
