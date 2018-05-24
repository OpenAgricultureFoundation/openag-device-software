
# Import device utilities
from device.utilities.logger import Logger
from device.utilities.error import Error
# from device.utilities.math import interpolate

# Import peripheral utilities
from device.peripherals.utilities import light

# Import device drivers
from device.drivers.dac5578.manager import DAC5578Manager as DAC5578


class Panel:
    """ An led panel controlled by a dac5578. """

    def __init__(self, name, bus, address, mux=None, channel=None, simulate=False):
        """ Instantiates panel. """

        # Instantiate logger
        self.logger = Logger(
            name = "LEDPanel({})".format(name),
            dunder_name = __name__,
        )
        
        # Instantiate name
        self.name = name

        # Instantiate driver
        self.dac5578 = DAC5578(
            name = name,
            bus = bus,
            address = address,
            mux = mux,
            channel = channel,
            simulate = simulate,
        )

        # Instantiate health & probe
        self.health = self.dac5578.health
        self.probe = self.dac5578.probe

        # Load in channel configs
        self.channel_configs = ...

 
    def initialize(self) -> Error:
        """ Initializes panel by probing driver with retry enabled. """
        error = self.dac5578.probe(retry=True)
        if error.exists():
            error.append("Panel initialization failed")
            self.logger.warning(error)
            return error
        else:
            return Error(None)


    def set_spd(self, desired_distance_cm, desired_intensity_watts, desired_spectrum_nm_percent):
        """ Sets spectral power distribution. """

        # Approximate spectral power disc
        try:
            channel_outputs, output_spectrum_nm_percent, output_intensity_watts = light.approximate_spd(
                channel_configs = self.channel_configs, 
                desired_distance_cm = desired_distance_cm, 
                desired_intensity_watts = desired_intensity_watts, 
                desired_spectrum_nm_percent = desired_spectrum_nm_percent,
            )
        except:
            error = Error("Unable to approximate spd due to light function failure")
            self.logger.exception(error.latest())


        error = self.set_outputs(channel_outputs)
        return channel_outputs, output_spectrum_nm_percent, output_intensity_watts


    def set_output(self, channel: int, percent: int) -> Error:
        """ Sets output on dac and checks for errors. """
        error = self.dac5578.set_output(channel, percent)
        if error.exists():
            error.append("Panel failed to set output")
            return error
        else:
            return Error(None)


    def set_outputs(self, outputs: dict) -> Error:
        """ Sets output channels to output percents. Only sets mux once. """
        error = self.core.set_outputs(outputs)
        if error.exists():
            error.append("Panel failed to set outputs")
            return error
        else:
            return Error(None)




    # desired_distance_cm = 5
    # desired_intensity_watts = 100
    # desired_spectrum_nm_percent = {
    #     "400-449": 10,
    #     "449-499": 10,
    #     "500-549": 30, 
    #     "550-559": 30,
    #     "600-649": 10,
    #     "650-699": 10}