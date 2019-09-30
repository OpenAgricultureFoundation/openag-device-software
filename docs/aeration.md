# Aeration
Aeration is the process by which air is circulated through, mixed with or dissolved in a liquid or substance. [1]

Within the controlled environment agriculture (CEA) context, aeration primarily refers to either soil aeration or water aeration for the purpose of increasing the oxygenation levels of the media.

Aeration and oxygenation SHOULD NOT be used interchangably, as aeration indicates dosing air, which is comprised of multiple gasses, and oxygenation only refers to dosing oxygen. In general, if air is being sourced from a particular environment, especially an ambient one, aeration is a more accurate descriptor. If oxygen is being dosed from a regulated tank, it would be appropriate to utilize the oxygenation descriptor.

The implementation for soil and water vary so each case will be handled separately, however they both should utilize the design paradigm of harware agnosticism. Hardware agnosticism dictates that the descriptor of the environmental conditions (i.e. in a recipe) must not be a function of a particular hardware implementation and must be physically generalizable. Without this property, sharing recipes between non-identical cultivation systems becomes impractical.

Within the aeration context, having a recipe simply describe an air pump to be on or off at a particular inverval does not embody the hardware agnostic paradigm since air pumps come in many varrying sizes that can dose air into media at varrying rates. The following sections detail an  implementation for aeration descriptors that are hardware agnostic and therefore easily sharable between non-identical cultivation systems.

## Water Aeration
Water aeration is the process of increasing or maintaining the oxygen saturation of water in both natural and artificial environments. [2]

Water aeration can be achieved in multiple ways, but for a reference implementation, we will consider an air pump attached to a tube and an air stone. This method pulls air from one particular region and pumps it through a porous air stone residing in the water of another region. The air stone is porous such that air flowing through it lets out in small air bubbles allowing the air contents to be absorbed by the water.

### Required Varaibles
To adequately describe a desired environment, such that aeration controllers can synthesize the environment, a recipe MUST include the following variables:
  1. Water Aeration Rate (liters/liters/minute) - This is a common unit used in bioreactors, sometimes referred to as "vvm". The first 'v' stands for volume of air (e.g. liter) ; the second 'v' stands for per unit of medium (e.g. liter); 'm' stands for per unit of time (e.g. minute). For example, 1 vvm (l/l/m) means in 1 minute time there is 1 liter of air passing through 1 liter of medium. [3]
  2. Water Aeration Period (minutes) - The time interval for the water aeration duty cycle
  3. Water Aeration Duty Cycle (percent) - The fraction of one period in which a signal or system is active. [4]
  4. Water Aeration Bubble Diameter (mm) - This is a function of the air stone. Some air stones create coarse bubbles (>2mm) and others fine (<2mm) which influence air absorption rates. [2]

Consider the example:
  1. Water Aeration Rate: 2 liter/liter/minute
  2. Water Aeration Period: 60 minutes
  3. Water Aeration Duty Cycle: 10 %
  4. Water Aeration Bubble Diameter: 10 mm

For the above example, assuming a pump with a dose rate of 2 liters/minute and a water reservoir volume of 1 liter, the air pump would be turning on at full power for 6 minutes then be off for the next 54 minutes, then back on for 6 minutes, then off for 54 minutes, and so on. Each time the pump turned on, it would be emitting bubbles with a 10 mm diameter.

### Non-Required Variables
The above required variables can be used for a rough approximation of aeration systems however, they do not fully capture the physical parameters associated with water aeration. The following variables MAY also be included when describing an environment utilizing aeration and SHOULD be utilized in high-precision cultivators:
  1. Water Aeration Source Temperature (Celsius) - What is the temperature of the air being pumped into the water?
  2. Water Aeration Source Humidity (%RH) - What is the relative humidity of the air being pumped into the water?
  3. Water Aeration Source Composition (gas:ppm) - What gasses are in the air that is being pumped into the water? Some systems pump from the air zone in the plant chamber, others pump from ambient air.

In practice, especially with lower-cost-lower-function devices, controlling these parameters are quite difficult, but observing them, or at lease making educated guesses about them, can become pragmatic.

Consider the example that sources air from a standard ambient environment:
  1. Water Aeration Source Temperature: 20 C
  2. Water Aeration Source Humidity: 40 %RH
  3. Water Aeration Source Composition (gas:ppm): {
    nitrogen: 780790,
    oxygen: 209445,
    argon: 9339,
    carbon_dioxide: 404,
    other: 22
  }

The source temperature and humidity are fairly strightforward but the source composition is based on generalized ambient conditions that can be used as default values for ambient environments. [5]

## Soil Aeration
WIP

## References
1. https://en.wikipedia.org/wiki/Aeration
2. https://en.wikipedia.org/wiki/Water_aeration
3. https://www.quora.com/What-is-meant-by-the-aeration-of-1VVM
4. https://en.wikipedia.org/wiki/Duty_cycle
5. http://www.uigi.com/air.html
