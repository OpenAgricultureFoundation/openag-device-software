import numpy, time


def magnitude(x):
    """ Gets magnitude of provided value. """

    # Check for zero condition
    if x == 0:
        return 0

    # Calculate magnitude and return
    return int(math.floor(math.log10(x)))


def interpolate(x_list, y_list, x):
    """ Interpolates value for x from x_list and y_list. """

    # Verify x_list and y_list are same length
    if len(x_list) != len(y_list):
        raise ValueError("x_list and y_list must be same length")

    # Verify x_list is sorted
    if not all(x_list[i] <= x_list[i+1] for i in range(len(x_list)-1)):
        raise ValueError("x_list must be sorted")

    # Verify x in range of x_list
    if x < x_list[0] or x > x_list[-1]:
        raise ValueError("x is not in range of x_list")

    # Check if x matches entry in x_list
    if x in x_list:
        index = x_list.index(x)
        return y_list[index]

    # Get index of smallest element greater than x
    for index in range(len(x_list)):
        if x_list[index] > x:
            break
    index = index - 1

    # Get values for calculating slope
    x0 = x_list[index]
    x1 = x_list[index + 1]
    y0 = y_list[index]
    y1 = y_list[index + 1]

    # Calculate slope
    m = (y1 - y0) / (x1 - x0)

    # Calculate interpolated value and return
    y = m * x
    return y


def discretize(minimum: int, maximum: int, value: float) -> dict:
    """ Discretizes a value across a range. """

    discretized_value = value / (maximum - minimum + 1)
    output = {}
    for counter in range(minimum, maximum + 1):
        output[counter] = discretized_value

    return output


def nnls(A, b, tol=1e-8):
    """ Origninal function by @alexfields

    Solve ``argmin_x || Ax - b ||_2`` for ``x>=0``. This version may be superior to the FORTRAN implementation when ``A`` has more rows than
    columns, and especially when ``A`` is sparse.
    Note that the arguments and return values differ from the FORTRAN implementation; in particular, this implementation does not expect the actual
    design matrix ``A`` nor the RHS vector ``b``, but rather ``A.T.dot(A)`` and ``A.T.dot(b)``. These are smaller than the original ``A`` and ``b``
    iff ``A`` has more rows than columns.
    This function also does not return the residual. The squared residual ``|| Ax-b ||^2`` may be calculated efficiently as:
        ``b.dot(b) + x.dot(A_dot_A.dot(x) - 2*A_dot_b)``
    where ``x`` is the output of this function

    """

    A_dot_A = A.T.dot(A)
    A_dot_b = A.T.dot(b)


    A_dot_A = numpy.asarray_chkfinite(A_dot_A)
    A_dot_b = numpy.asarray_chkfinite(A_dot_b)

    if len(A_dot_A.shape) != 2:
        raise ValueError("expected matrix")
    if len(A_dot_b.shape) != 1:
        raise ValueError("expected vector")

    nvar = A_dot_A.shape[0]
    if nvar != A_dot_A.shape[1]:
        raise ValueError("expected square matrix")

    if nvar != A_dot_b.shape[0]:
        raise ValueError("incompatible dimensions")

    P_bool = numpy.zeros(nvar, numpy.bool)
    x = numpy.zeros(nvar, dtype=A_dot_A.dtype)
    s = numpy.empty_like(x)
    w = A_dot_b
    while not P_bool.all() and w.max() > tol:
        j_idx = w[~P_bool].argmax()
        newly_allowed = numpy.flatnonzero(~P_bool)[j_idx]
        P_bool[newly_allowed] = True
        s[:] = 0
        currPs = numpy.flatnonzero(P_bool)
        if len(currPs) > 1:
            s[currPs] = numpy.linalg.solve(A_dot_A[currPs[:, None], currPs[None, :]], A_dot_b[currPs])
        else:
            currP = currPs[0]
            s[currP] = A_dot_b[currP]/A_dot_A[currP, currP]
        s_P_l_0 = (s[currPs] < 0)
        while s_P_l_0.any():
            currPs_s_P_l_0 = currPs[s_P_l_0]
            alpha = (x[currPs_s_P_l_0]/(x[currPs_s_P_l_0] - s[currPs_s_P_l_0])).min()
            x += alpha*(s-x)
            P_bool[currPs] = (x[currPs] > tol)
            s[:] = 0
            currPs = numpy.flatnonzero(P_bool)
            if len(currPs) > 1:
                s[currPs] = numpy.linalg.solve(A_dot_A[currPs[:, None], currPs[None, :]], A_dot_b[currPs])
            else:
                currP = currPs[0]
                s[currP] = A_dot_b[currP]/A_dot_A[currP, currP]
            s_P_l_0 = (s[currPs] < 0)
        x[:] = s[:]
        if x[newly_allowed] == 0:
            break  # avoid infinite loop
        w = A_dot_b - A_dot_A.dot(x)
    return x


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


def calculate_desired_spd(intensity_watts, spectrum_nm_percent):
    """ Calculates desired spd. """
    for wavelength_band, percent in spectrum_nm_percent.items():
        spectrum_nm_percent[wavelength_band] = percent * intensity_watts
    return spectrum_nm_percent


def get_intensity_at_distance(channel_config, distance):
    """ Gets intensity (watts) at illumination distance (cm). """
    planar_distance_map = channel_config["planar_distance_map"]
    distance_list = []
    intensity_list = []
    for entry in planar_distance_map:
        distance_list.append(entry["distance_cm"])
        intensity_list.append(entry["intensity_watts"])
    intensity = interpolate(distance_list, intensity_list, distance)
    return intensity


def discretize_spd(spd):
    """ Discretizes channel spd. Converts values banded by wavelengths greater
        than 1 nm into a set of wavelengths at 1nm granularity with corresponding
        value. """
    discretized_spd = {}
    for wavelength_band, intensity in spd.items():
        minimum, maximum = list(map(int, wavelength_band.split("-")))
        discretized_spd.update(discretize(minimum, maximum, intensity))
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
        print(translated_channel_spd)

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
    weighted_channel_outputs = nnls(channel_spd_matrix, desired_spd_vector)

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


def dictify_output_spd_vector(desired_spd, output_spd_vector):
    """ Converts output spd vector into its dictionary representation. """
    output_spd_dict = {}
    index = 0
    for wavelength_band, _ in desired_spd.items():
        output_spd_dict[wavelength_band] = output_spd_vector[index]
        index += 1
    return output_spd_dict


if __name__ == '__main__':

    desired_distance_cm = 5
    desired_intensity_watts = 100
    desired_spectrum_nm_percent = {
        "400-449": 10,
        "449-499": 10,
        "500-549": 30, 
        "550-559": 30,
        "600-649": 10,
        "650-699": 10}

    desired_spd = calculate_desired_spd(
        intensity_watts = desired_intensity_watts,
        spectrum_nm_percent = desired_spectrum_nm_percent
    )
    print(desired_spd)

    channel_spd_matrix = build_channel_spd_matrix(
        channel_configs = channel_configs,
        distance = desired_distance_cm,
        desired_spd = desired_spectrum_nm_percent,
    )
    print(channel_spd_matrix)

    desired_spd_vector = build_desired_spd_vector(
        desired_spectrum_nm_percent = desired_spectrum_nm_percent, 
        desired_intensity_watts = desired_intensity_watts,
    )
    print(desired_spd_vector)

    channel_output_vector = calculate_channel_output_vector(
        channel_spd_matrix = channel_spd_matrix, 
        desired_spd_vector = desired_spd_vector,
    )
    print(channel_output_vector)

    channel_output_dict = dictify_channel_output_vector(
        channel_configs = channel_configs,
        channel_output_vector = channel_output_vector,
    )
    print(channel_output_dict)

    output_spd_vector = calculate_output_spd(
        channel_spd_matrix = channel_spd_matrix,
        channel_output_vector = channel_output_vector, 
    )
    print(output_spd_vector)


    output_spd_dict = dictify_output_spd_vector(
        desired_spd = desired_spd,
        output_spd_vector = output_spd_vector,
    )
    print(output_spd_dict)

