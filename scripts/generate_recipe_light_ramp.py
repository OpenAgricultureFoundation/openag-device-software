
NUM_ENTRIES = 12
CYCLE_DURATION_MINUTES = 1
INTENSITY_INCREMENT_PAR = 50

# Generate phases
print("\n~~~ ENVIRONMENTS ~~~")
spectrum = '\t"light_spectrum_nm_percent": {"380-399": 0, "400-499": 18, "500-599": 32, "600-700": 36, "701-780": 14},\n'
distance = '\t"light_illumination_distance_cm": 73,\n'
for i in range(1, NUM_ENTRIES + 1):
    par = INTENSITY_INCREMENT_PAR * i
    key = '"light_{}": '.format(par)
    name = '\t"name": "Light {}",\n'.format(par)
    intensity = '\t"light_ppfd_umol_m2_s": {}\n'.format(par)
    entry = key + "{\n" + name + spectrum + distance + intensity + "},"
    print(entry)

# Generate morning cycles
print("\n~~~ MORNING CYCLES ~~~")
duration = '\t"duration_minutes": {}\n'.format(CYCLE_DURATION_MINUTES)
for i in range(1, NUM_ENTRIES + 1):
    par = INTENSITY_INCREMENT_PAR * i
    name = '\t"name": "Morning {}/{}",\n'.format(i, NUM_ENTRIES)
    environment = '\t"environment": "light_{}",\n'.format(par)
    entry = "{\n" + name + environment + duration + "},"
    print(entry)

# Generate evening cycles
print("\n~~~ EVENING CYCLES ~~~")
duration = '\t"duration_minutes": {}\n'.format(CYCLE_DURATION_MINUTES)
for i in range(1, NUM_ENTRIES + 1):
    par = 600 - INTENSITY_INCREMENT_PAR * i
    name = '\t"name": "Evening {}/{}",\n'.format(i, NUM_ENTRIES)
    environment = '\t"environment": "light_{}",\n'.format(par)
    entry = "{\n" + name + environment + duration + "},"
    print(entry)
