# Phased Environment v1 Recipe Format
This recipe format allows for environment states to be defined and referenced
from an unspecified number of cycles in an unspecified number of phases. Each 
phase can contain multiple cycles that can be repeated a specified number of
times.

## Reference Information
It also includes reference information such as recipe name, description, 
universally unique id (uuid), parent uuid, supporting uuids, creation 
timestamp, and authors.

## UUIDs
The usage of UUIDs allows for new recipes to be created from an offline state
then uploaded to a central database upon future connection without having 
conflicting IDs. 


## Cultivars and Variables
Additional information included in this format required for consistent recipe replication includes the cultivars and variables used throughout the recipe.

### Cultivars
Each cultivar used contains information on name, description, purchase link, 
average size and average cultivation duration. A uuid is also included so a 
global database of cultivars can be generated as more experiments are ran
over time. Furthermore, the cultivar parameter is a list to accomodate multi-cropping use cases.

### Variables
Each variable used contains information on name, unit, and description to 
enhance clarity for the recipe designer and support dynamic UI renderings
of variable objects. For example, a UI will be able to dynamically load an 
air temperature icon if a new, known, sensor is installed. Without this, 
custom one-off UIs will need to be designed for each device configuration.

Furthermore, a uuid is also included in the variable information dictionary
so a global database of non-redundant variables can be generated as  
system capabilities evolve. Avoiding redundancy is important for recipe 
inter-operability. For example, a device with a control loop configured to 
drive the `air_temperature_celsius` variable would not be able to run a recipe 
that specifies an `air_temp_celsius` setpoint.

## General Mindset
As a general mindset, it is important to view the recipe as a definition of 
all relavent environmental conditions influincing the expression of the 
cultivar's traits to be able to share recipes across devices that do not 
necessarily have the same hardware configurations.

## Use Case
Consider the case where a recipe is created on a device with a small heating element then shared to a similar device with a large heating element. If the 
recipe simply dictates to `turn the heater on for 10 minutes every hour` the 
temperatures in each device will be different and result in a different 
expression of cultivar traits.

## Hardware Agnostic
Therefore, recipes must be hardware agnostic and speak the language of climate.
A more appropriate device command would be `set the temperature to 20 celsius 
until hearing otherwise`. As cost is a constraint for many devices, having a 
physical sensor for every actuator is not always pragmatic, however much can 
be reasoned about an actuators influence on the environment it is actuating 
upon provided there is sufficient information available on such environment.

## Pseudo Sensor
For example, if a heater controller is provided the volume, anticipated 
ambient temperature conditions, chamber insulation value, and heat exhchange 
events (e.g. light panel reports adding 40 BTUs to system when on), the 
controller  will be able to make a reasonable estimate with a certainty metric 
of the temperature in the box and can drive the heater after calculating
this `pseudo-sensor` value.

## Device Config
To generate this pseudo-sensor value, information on device config is requied
and must be included in each device. Thus each device will have a `config` file
to accompany the `recipe` file. More information on config files is out of scope for this document, but references will be provided.

## Qualifications
To qualify, the heater use case, temperature sensors are generally low cost
and easy to integrate into systems, and the example only serves to 
illustrate a point. However, in practice, high quality light sensors are quite expensive and non-obvious to integrate and will utilize this recipe format
feature.

## Cultivation Method
The remaining information required for consistent recipe replication is the cultivation method since a plant grown with a hydroponic cultivation method will realize different traits than a soil-based method. This same idea holds true within hydroponic and soil-based methods. For example, a cultivar grown in a shallow water culture system will not be subjected to the same environmental conditions as a high-pressure aeoponic system.

## More Information
For more information on the `phased-environment-v1` recipe format see the 
[Phased Environment V1 Example Recipe](phased_environment_v1_example_recipe.json)