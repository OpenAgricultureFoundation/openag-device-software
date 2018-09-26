# Light Overview
The light control software is one of the more complex modules in the codebase and warrants explanation beyond in-line comments to convey the ideas as clearly and fully as possible.

## Contents
1. [Background](#background)
	1. [Hardware Agnostic](#hardware-agnostic)
	2. [Heater Example](#heater-example)
	3. [Lighting Intro](#lighting-intro)
	4. [Light Field Modelling](#light-field-modelling)
	5. [Spectral Power Distribution](#spectral-power-distribution-spd)
	6. [Photosynthetically Active Radiation](#photosynthetically-active-radiation-par)
	7. [SPD = Spectrum * Intensity](#spd-is-spectrum-times-intensity)
	8. [Illumination Distance](#illumination-distance)
	9. [Illumination Distance Considerations](#illumination-distance-considerations)
	10. [Illumination Distance Approximation](#illumination-distance-approximation)
	11. [Universal Light Recipe Format](#universal-light-recipe-format-ulrf)
2. [Modelling](#modelling)
	1. [ULRF -> Setpoints](#ulrf-to-setpoints)
	2. [Ax=b](#axb)
	3. [Example Problem](#example-problem)
	4. [Solving Ax=b](#solving-axb)
	5. [Example Soltion](#example-solution)
	6. [Setpoint Caveats](#setpoint-caveats)
	7. [Shortcomings of Ordinary Least Squares Approximation](#shortcomings-of-ordinary-least-squares-approximation)
	8. [Redundant Channels](#redundant-channels)
3. [Calibration](#calibration)
	1. [Overview](#overview)
	2. [Distance Map](#distance-map)
	3. [Channel Spectrum & Intensity](#channel-spectrum-and-intensity)
	4. [DAC Map](#dac-map)
	5. [Verification](#verification)
4. Data
	1. Taurus [PDF](taurus_calibration_verification.pdf) | [XLSX](taurus_calibration_verification.xlsx)
	2. Orion

## Background
This is an in-depth overview of the relavent considerations used when developing the lighting model and resulting recipe format.

### Hardware Agnostic
The light control software is an embodiment of the pursuit towards `hardware agnostic recipes`. A recipe is hardware agnostic if it can run on any device irrespective of the hardware sub-systems. 

### Heater Example
Consider the case where two devices are identical except for one having a heater double in size of the other. If a recipe were to dictate `heater on for 5 minutes every hour` the two devices would create different environmental conditions and would not be creating the same stressors influencing the expression of the organism being cultivated. This introduces the idea of `replicability` -- one of the most import considerations in developing recipes is being able to run the same recipe on different bots and yield the same resulting organismal expressions. If the information describing the environmental conditions, a crucial part in the language of recipes, is inadequate to model environmental conditions over time, replicating environments will be untenable and as a result replicating organisms as well.

### Lighting Intro
So then how to handle the case of our mismatched heaters? In practice, temperature sensors are cheap and can be easily used to create a `closed-loop` controller where the actuator output is a function of the sensor input. However, with lighting, sensors are much more costly and are accompanied by a suite of problems. Simple lux sensors are cheap but only give an intensity relative to a known light source so if that light source is dynamic, e.g. has multiple channels (like our light panels), it will be of little help to model the light field in the grow area. The best they can be used for is to calibrate the light panel over time as the lights `burn in` but that consideration is for a later development stage. Embedding light sensors in the environment has problems with spacial resolution and canopy occlusion if the sensor is in a fixed position or else requires a complex electromechanical assembly for the sensor to be in a movable position.

### Light Field Modelling
The best way we have found to model the light field in the grow area is to measure our light panels with a `spectrometer` and to operate them with `open-loop` control where the actuator makes assumptions about itself and does not incorporate sensor feedback. In the heater example this is analagous to describing how much heat is added to an environment. It is common for many heaters to use the BTU, a metric describing the amount of heat required to raise the temperature of one pound of water by one degree Fahrenheit. It is a way to make the environmental conditions more consistent in pursuit of `replicability` when closed loop control is not an option. Note: For open-loop heating there are many other concerns to achieve this (insulation, external environment temperature, etc.) but that is not the point of this example.

### Spectral Power Distribution (SPD)
The next logical question is, "What is the equivalent unit to a BTU for the lighting context?" To answer this, it is important to understand the concept of `spectral power distribution.` In every light source there is a spectral power distribution, or SPD for short. The SPD is effectively a chart of spectral region (wavelength) vs. power / unit area. An intuitive way to think about this is to view the light source through a prism that splits the source into individual colors where each color is of varrying intensity depending on the  source composition. For example a warm white light has a more intense red color and cool white light has a more intense blue color but both sources have many other colors as well, just at a lower intensity.

### Photosynthetically Active Radiation (PAR)
In the plant cultivation context, the relevant spectral region is that of `photosynthetically active radiation`, or PAR for short. The PAR spectral region, or band of wavelengths, is between 400-700 nanometers. This band is considered the PAR band because it corresponds to the wavelenghths that photosynthetic organisms are able to use in the process of photosynthesis.

### SPD is Spectrum times Intensity
Spectral power distributions can be deconstructed into two parts: 1. Spectrum 2. Intensity. The spectrum is the normalized SPD (i.e. 0-100%) and the intensity is the magnitude of the SPD. So, by multiplying the spectrum by the intensity will result in the SPD.

### Illumination Distance
The SPD is the most important element to describe the light field but there is another crucial factor: `illumination distance`. The intensity from a point light source follows an inverse square relationship so the further away an object is from the source, the less intense it is at an exponentially decreasing rate.

### Illumination Distance Considerations
Illumination distance is deceptively simple but is a worthy consideration for modelling light fields in cultivation chambers. The big question is, "Distance from where to what?" and the all-encompasing answer is from the light source to every point on the surface of the plant (top-canopy, sub-canopies, stems, indivudual leaves, etc.) but that is a modelling nightmare and will require a seperate vain of develpment to achieve well. The rough metric that is commonly used in the plant science community is simply distance from illumination source to top canopy and is what we use (as of Sept. 2018) for modelling our light fields.

### Illumination Distance Approximation
The illumination distance metric defined as distance from illumination source to top canopy  is not a great approximation for indoor lighting as light sources are much closer to the plants than the light source in outdoor cultivation (the Sun). As a result of the inverse square relationship, for outdoor cultivation, the intensity at the top of the plant and the bottom of the plant (canopy occulsion ignored) is effectively the same since the Sun is so far away from the Earth. However, this is not true for indoor lighting since the lights are much closer. However, since illumination distance is a function of the light model, the best intermediary solution is to reference the light calibrations and compute the adjusted light field when needed.

### Universal Light Recipe Format (ULRF)
By now, we have been introduced to the 3 main elements to specify the light field in an environmental recipe: 1. Spectrum 2. Intensity 3. Distance. We consider these elements as the `universal light recipe format` (ULRF) since they are easy to specify in a recipe and are able to adequately model the light field in a hardware agnostic and replicable way. They currently look like this is a recipe:

```
"light_spectrum_nm_percent": {"380-399": 0.0, "400-499": 0.0, "500-599": 0.0, "600-700": 100.0, "701-780": 0.0},
"light_ppfd_umol_m2_s": 300,
"light_illumination_distance_cm": 10
```

There can be as many spectral bands as desired in whatever range, but the important constraint is that the associated values must add up to 100%. These are the default ranges as they correspond to Ultraviolet (380-399), Blue (400-499), Green (500-599), Red (600-700), and Far Red (701-780). 

Light ppfd is effectively intensity but has a slightly more correct variable name as intensity is a bit vague and photosynthetic photon flux density (PPFD) is precisely what we are measuring when taking light calibrations. This metric is colloquially referred to simply as the PAR value.


## Modelling
This is the specifics on how we model light sources and solve for individual channel outputs from the ULRF.

### ULRF to Setpoints
Currently our light panels have multiple channels each with a different color LED (Far Red, Red, Green, Blue, Warm White, Cool White). By varrying the power to each channel, we can approximate the desired light field in the box. The big question is how do we solve for these channel `setpoints.` 

### Ax=b
We solve this by modelling each channel of the light panel and computing its SPD at the desired distance. Each channel SPD can be considered a vector and by using channel SPDs as the columns in a matrix we can reduce the problem to the fundamental problem of linear algebra, Ax=b, solve for x.
```
A = Channel SPD Matrix
x = Channel Setpoint Vector
b = Desired SPD Vector
```

Basically we are trying to solve for the channel weightings that will sum the individual channel SPDs to best approximate the desired SPD vector.

### Example Problem
Pretend we have a panel with 3 channels: Red, Green, and Blue that correspond perfectly to their spectral bands and all have the same intensity at 10cm of 200 umol/m2/s. These channel SPD spectrums and intensities would look like:
```
# {"380-399": <UV>, "400-499": <Blue>, "500-599": <Green>, "600-700": <Red>, "701-780": <Far Red>}
R_Spectrum = {"380-399": 0, "400-499": 0, "500-599": 0, "600-700": 100, "701-780": 0} # nm: percent
R_Intensity = 200 # umol/m2/s
G_Spectrum = {"380-399": 0, "400-499": 0, "500-599": 100, "600-700": 0, "701-780": 0} # nm: percent
G_Intensity = 200 # umol/m2/s
B_Spectrum = {"380-399": 0, "400-499": 100, "500-599": 0, "600-700": 0, "701-780": 0} # nm: percent
B_Intensity = 200 # umol/m2/s
```
And their corresponding SPD dictionaries:
```
# {"380-399": <UV>, "400-499": <Blue>, "500-599": <Green>, "600-700": <Red>, "701-780": <Far Red>}
R = {"380-399": 0, "400-499": 0, "500-599": 0, "600-700": 200, "701-780": 0}
G = {"380-399": 0, "400-499": 0, "500-599": 200, "600-700": 0, "701-780": 0}
B = {"380-399": 0, "400-499": 200, "500-599": 0, "600-700": 0, "701-780": 0}
```
And their corresponding SPD vectors:
```
# [<UV>, <Blue>, <Green>, <Red>, <Far Red>]
R = [0, 0, 0, 200, 0]
G = [0, 0, 200, 0, 0]
B = [0, 200, 0, 0, 0]
```
And their corresponding SPD matrix:
```
A = [R, G, B]
# A =  0   0   0
#      0   0  200
#      0  200  0
#     200  0   0
#      0   0   0
```
If we desire a completely red spectrum at 50 umol/m2/s, the desired SPD vector is:
```
b = [0, 0, 0, 50, 0]
```
We now have A and b and can solve for X, but there are a few constraints.

### Solving Ax=b
To solve Ax=b the easiest way to do that is to invert A and multibly b by it. This process looks something like this:
```
Ax=b
A'Ax=A'b
x = A'b
```
This is great if A is invertible, i.e. is a square matrix but that is not a fair assumption for us to make as we want to be able to solve for ANY spectral bands for ANY number of channels. In this context a good first solver is to use a least squares (LSQ) approximation.

### Example solution
The solution to the example problem is trivial and doesn't actually require a LSQ but there are plenty of resources for understanding LSQ in the context of linear algebra. Or you could just look at the code. The example solution is:
```
# x = [R_Setpoint, G_Setpoint, B_Setpoint]
x = [25 0  0] # percent
```
The solution can be interpreted as follows: "To realize the desired SPD requires the red channel to be at 25% intensity, green at 0% intensity, and blue at 0% intensity"

### Setpoint Caveats
The setpoints from solving Ax=b refer to the channel light output intensity. In an ideal context the intensity sent to the light channel would correspond 1:1 but that is not a fair assumption. Depending on the hardware circuitry setting the LED controller intensity, usually a voltage output from a digital to analog converter (DAC) to a current regulator does not correspond perfectly to the output light intensity. As a result there is a final translation that must happen to map the "PAR" setpoint to the "DAC" setpoint.

### Shortcomings of Ordinary Least Squares Approximation
Ordinary least squares approximation solvers operate in math land and yield a few un-realizable setpoints in hardware land. The two main problems are 1. Setpoints cannot be negative -- we cannot take light away. 2. Setpoints cannot be more than 100% -- we cannot have more than 100% light output.

To solve these, we use a non-negative LSQ for (1) and a bounded LSQ for (2) resulting in the final solver we use which is a bounded non-negative least squares approximation (BNNLS).

### Redundent Channels
In some cases there are multiple channels of the same type (i.e. using multiple cool white leds to get higher intensities in sun-like spectrums). For hardware performance and environmental homogeneity it is best have replicated channels be at the same setpoint. Therefore before solving, we reduce the channel instances to channel types, adjust the corresponding spd, solve Ax=b, then unpack the types back into the instances.

## Calibration
Now that we have an understanding of the problem and the computational solution, we need to acquire the physical measurements to calibrate and verify the model. This section explains the methods to perform such acquisition and verification.

### Overview
To perform the following computations we need the following:
1. Distance Map - PAR output for entire panel as a function of distance
2. Channel Spectrums - Spectrum for individual channels
3. Channel Relative Intensities - Individual channel relative intensities to total intensity
4. DAC Map - Mapping between dac setpoint and par setpoint

### Distance Map
*Objective:* Determine relationship between illumination distance and PAR output for a single panel.

*Procedure:* At the center of the panel, with all channels fully powered, and with all other panels off, measure total and segmented PAR (umol) for distance in range in increments of approximately 5cm.

*Questions:* Is the spectrum consistent across illumination distances? Is there a distinct point where the spectrum becomes inconsistent?

### Channel Spectrum and Intensity
*Objective:* Determine the spectrum and relative intensity for each light channel type.

*Procedure:* At a fixed distance from a single panel where the overall spectrum is consistent (reference distance calibration test) and total PAR output highest, at the center of the panel, with all other lights off, cycling through channel types, where for each channel type all channels of that type are powered fully, measure total and segmented PAR (umol).

*Questions:* What is the relative spectrum percents and intensities for each channel type?

### DAC Map
*Objective:* Determine relationship between DAC output and PAR output for a single panel. 

*Procedure:* At a fixed distance from a single panel where the overall spectrum is consistent (reference distance calibration test) and total PAR output highest, at the center of the panel, with all other lights off, and all channels at the same level, measure total and segmented PAR (umol) for DAC output range in increments of 5%.

*Questions:* Is the spectrum consistent across DAC ouputs? If so, determine the lookup table for mapping DAC voltage output % to panel relative PAR output %.

### Verification
*Objective:* Verify reported spectrum and intensity are accurate for multiple spectrums, intensities and distances.

*Procedure:* Compare reported and measured for 3 spectrums, 3 distances, and 3 intensities that are likely to be used in normal operation.

*Questions:* Does the algorithmically reported intensity and spectrum match the measured intensity and spectrum for multiple spectrums, intensities, and distances? How well?
