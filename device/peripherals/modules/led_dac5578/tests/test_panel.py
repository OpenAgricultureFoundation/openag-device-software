# Import standard python libraries
import sys, os, json

# Import module...
try:
	# ... if running tests from project root
	sys.path.append(".")
	from device.peripherals.modules.led_dac5578.panel import Panel
except:
	# ... if running tests from same dir as panel.py
	sys.path.append("../../../../")
	from device.peripherals.modules.led_dac5578.panel import Panel

# Change directory for importing files
os.chdir("../../../../")

# Import test peripheral setup
peripheral_setup = json.load(open("device/peripherals/modules/led_dac5578/tests/wsetup.json"))
channel_configs = peripheral_setup["channel_configs"]


# Set desired setpoints
desired_distance_cm = 5
desired_intensity_watts = 100
desired_spectrum_nm_percent = {
    "400-449": 10,
    "449-499": 10,
    "500-549": 30, 
    "550-559": 30,
    "600-649": 10,
    "650-699": 10}


def test_init():
	panel = Panel(
		name = "Test",
		channel_configs = channel_configs,
		bus = 2,
		address = 0x47,
		mux = 0x77,
		channel = 0,
		simulate = True,
	)


def test_initialize():
	panel = Panel("Test", channel_configs, 2, 0x47, mux = 0x77, channel = 0, simulate = True)
	panel.initialize()


def test_set_output():
	panel = Panel("Test", channel_configs, 2, 0x47, mux = 0x77, channel = 0, simulate = True)

	# Standard case
	error = panel.set_output("FR", 90.0)
	assert error.exists() == False

	# Unknown channel
	error = panel.set_output("XX", 90.0)
	assert error.exists() == True


def test_set_outputs():
	panel = Panel("Test", channel_configs, 2, 0x47, mux = 0x77, channel = 0, simulate = True)

	# Standard case
	outputs = {"FR": 10, "WW": 50}
	error = panel.set_outputs(outputs)
	assert error.exists() == False


def test_set_spd():
	panel = Panel("Test", channel_configs, 2, 0x47, mux = 0x77, channel = 0, simulate = True)
	channel_outputs, output_spectrum_nm_percent, output_intensity_watts, error = panel.set_spd(
		desired_distance_cm = desired_distance_cm, 
		desired_intensity_watts = desired_intensity_watts, 
		desired_spectrum_nm_percent = desired_spectrum_nm_percent,
	)
	assert error.exists() == False
	assert channel_outputs == {'FR': 46.0, 'WW': 54.0}
	assert output_spectrum_nm_percent == {'400-449': 12.27, '449-499': 12.27, '500-549': 42.44, '550-559': 8.49, '600-649': 12.27, '650-699': 12.27}
	assert output_intensity_watts == 81.52
