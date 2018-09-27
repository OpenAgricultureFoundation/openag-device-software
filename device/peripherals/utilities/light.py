# Import standard python modules
import numpy

# Import python types
from typing import Dict, Any, List, Tuple

# Import device utilities
from device.utilities import maths
from device.utilities import accessors


def approximate_spd(
    panel_properties: Dict[str, Any],
    des_distance: float,
    des_intensity: float,
    des_spectrum: Dict[str, float],
) -> Tuple[Dict, Dict, float]:
    """Approximates spectral power distribution."""

    # Get desired spd vector (i.e. `b` in Ax=b)
    desired_spd_dict = calculate_spd_dict(des_intensity, des_spectrum)
    desired_spd_vector = accessors.vectorize_dict(desired_spd_dict)

    # Get channel spd matrix (i.e. `A` in Ax=b)
    raw_channel_spd_ndict = build_channel_spd_ndict(panel_properties, des_distance)
    channel_spd_ndict = translate_spd_ndict(raw_channel_spd_ndict, desired_spd_dict)
    channel_spd_matrix = accessors.matrixify_nested_dict(channel_spd_ndict)

    # Get channel setpoints (i.e `x` in Ax=b)
    channel_setpoint_vector = solve_setpoints(channel_spd_matrix, desired_spd_vector)
    channel_setpoint_list = []
    for setpoint in channel_setpoint_vector:
        channel_setpoint_list.append(setpoint * 100)
    channel_types = panel_properties.get("channel_types", {})
    channel_setpoint_dict = accessors.dictify_list(channel_setpoint_list, channel_types)

    # Get output spd, spectrum, and intensity
    output_spd_list = calculate_output_spd(channel_spd_matrix, channel_setpoint_vector)
    output_spectrum_list, output_intensity = deconstruct_spd(output_spd_list)
    output_spectrum_dict = accessors.dictify_list(
        output_spectrum_list, desired_spd_dict
    )

    # Map channel setpoints from channel types to channel instances
    mapped_channel_setpoint_dict = {}
    channels = panel_properties.get("channels", {})
    for channel_name, channel_entry in channels.items():
        key = channel_entry.get("type")
        setpoint = channel_setpoint_dict.get(key, 0)
        mapped_channel_setpoint_dict[channel_name] = round(setpoint, 2)

    # Successfully approximated spectral power distribution
    return mapped_channel_setpoint_dict, output_spectrum_dict, output_intensity


def calculate_spd_dict(intensity: float, spectrum: Dict[str, float]) -> Dict:
    """Calculates spd dict from intensity and spectrum."""
    spd_dict = {}
    for wavelength_band, percent in spectrum.items():
        spd_dict[wavelength_band] = intensity * percent / 100.0
    return spd_dict


def build_channel_spd_ndict(
    panel_properties: Dict[str, Any], distance: float
) -> Dict[str, Dict[str, float]]:
    """Builds channel spd nested dict."""

    # Initialize channel property variables
    channels = panel_properties.get("channels", {})
    channel_types = panel_properties.get("channel_types", {})
    intensity_map = panel_properties.get("intensity_map_cm_umol", 0)

    # Get channel weights
    channel_weights: Dict[str, float] = {}
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
    spd_ndict: Dict[str, Dict[str, float]], reference_spd_dict: Dict[str, float]
) -> Dict[str, Dict[str, float]]:
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
    translated_spd_dict: Dict[str, float] = {}
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


def solve_setpoints(
    channel_spd_matrix: numpy.ndarray, desired_spd_vector: numpy.ndarray
) -> List[float]:
    """Solves for channel setpoints with a bounded non-negative least squares solver."""
    raw_setpoint_list = maths.bnnls(channel_spd_matrix, desired_spd_vector)
    setpoint_list = []
    for setpoint in raw_setpoint_list:
        setpoint_list.append(round(setpoint, 3))
    return setpoint_list


def calculate_output_spd(
    channel_spd_matrix: numpy.ndarray, channel_output_vector: List[float]
) -> List[float]:
    """Calculates ouput spectral power distribution."""
    raw_output_spd = channel_spd_matrix.dot(channel_output_vector)
    output_spd = []
    for element in raw_output_spd:
        output_spd.append(round(element, 3))
    return output_spd


def deconstruct_spd(spd_list: List[float]) -> Tuple[List[float], float]:
    """Deconstructs spd into spectrum and intensity."""
    intensity = sum(spd_list)
    rounded_intensity = float("{:.2f}".format(intensity))
    spectrum_list = []
    for element in spd_list:
        if intensity != 0:
            value = float(element) / intensity * 100.0
        else:
            value = 0
        rounded_value = float("{:.2f}".format(value))
        spectrum_list.append(rounded_value)
    return spectrum_list, rounded_intensity


def calculate_ulrf_from_percents(
    panel_properties: Dict[str, str],
    channel_setpoints: Dict[str, float],
    distance: float,
) -> Tuple[Dict, float, float]:
    """Calculates universal light recipe format (ULRF) for provided channel 
    configuration, channel power percents, and illumination distance."""

    # Get min/max distance for channels
    intensity_map = panel_properties.get("intensity_map_cm_umol", {})
    distance_list = []
    intensity_list = []
    for distance_, intensity in intensity_map.items():  # type: ignore
        distance_list.append(float(distance_))
        intensity_list.append(intensity)

    min_distance = min(distance_list)
    max_distance = max(distance_list)

    # Check distance in range, else use extrema
    if distance > max_distance:
        distance = max_distance
    if distance < min_distance:
        distance = min_distance

    # Get reference SPD from channel configs
    channel_types = panel_properties.get("channel_types", {})
    for channel_key, channel_dict in channel_types.items():  # type: ignore
        reference_spectrum = channel_dict.get("spectrum_nm_percent", {})
        break

    # Calculate resultant spectrum and intensity from channel power percents
    spectrum, intensity = calculate_resultant_spd(
        panel_properties, reference_spectrum, channel_setpoints, distance
    )

    return spectrum, intensity, distance


def calculate_resultant_spd(
    panel_properties: Dict[str, Any],
    reference_spd_dict: Dict[str, float],
    channel_setpoint_dict: Dict[str, float],
    distance: float,
) -> Tuple[Dict[str, float], float]:
    """Calculates spd from provided channel outputs at distance. Returns 
    spd with the same spectral bands as the reference spd."""

    # Parse channel properties
    channels = panel_properties.get("channels", {})

    # Get channel spd matrix
    raw_channel_spd_ndict = build_channel_spd_ndict(panel_properties, distance)
    channel_spd_ndict = translate_spd_ndict(raw_channel_spd_ndict, reference_spd_dict)
    channel_spd_matrix = accessors.matrixify_nested_dict(channel_spd_ndict)

    # Factorize setpoint types. The type setpoint is the average of all instance setpoints
    factorized_channel_setpoint_dict: Dict[str, float] = {}
    count: Dict[str, int] = {}
    for channel_name, setpoint in channel_setpoint_dict.items():
        channel_dict = channels.get(channel_name, {})
        channel_type = channel_dict.get("type", "Error")
        if channel_type in factorized_channel_setpoint_dict:
            prev_setpoint = factorized_channel_setpoint_dict[channel_type]
            weighted_prev_setpoint = prev_setpoint * count[channel_type]
            count[channel_type] += 1
            new_setpoint = (weighted_prev_setpoint + setpoint) / count[channel_type]
            factorized_channel_setpoint_dict[channel_type] = new_setpoint
        else:
            factorized_channel_setpoint_dict[channel_type] = setpoint
            count[channel_type] = 1

    # Get channel setpoint vector
    channel_setpoint_list = accessors.listify_dict(factorized_channel_setpoint_dict)
    channel_setpoint_vector = []
    for setpoint_percent in channel_setpoint_list:
        setpoint_decimal = setpoint_percent / 100.0
        channel_setpoint_vector.append(setpoint_decimal)

    # Get output spd, spectrum, and intensity
    output_spd_list = calculate_output_spd(channel_spd_matrix, channel_setpoint_vector)
    output_spectrum_list, output_intensity = deconstruct_spd(output_spd_list)
    output_spectrum_dict = accessors.dictify_list(
        output_spectrum_list, reference_spd_dict
    )

    return output_spectrum_dict, output_intensity
