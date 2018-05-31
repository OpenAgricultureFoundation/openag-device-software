# Import standard python modules
import logging, time, threading
from typing import Optional, Tuple, Dict

# Import device utilities
from device.utilities.modes import Modes
from device.utilities.error import Error


class Atlas:
    """ Parent class for atlas drivers. """


    def process_command(self, command_string: str, processing_seconds: float, 
            num_response_bytes: int = 31, read_retry: bool = True, 
            read_response: bool = True):
        """ Sends command string to device, waits for processing seconds, then
            tries to read num response bytes with optional retry if device
            returns a `still processing` response code. Read retry is enabled 
            by default. Returns response string on success or raises exception 
            on error. """
        self.logger.debug("Processing command: {}".format(command_string))

        # Send command to device
        byte_array = bytearray(command_string + "\00", 'utf8')
        error = self.i2c.write_raw(byte_array)

        # Check for errors
        if error.exists():
            error.report("Driver unable to process command")
            return None, error

        # If read enabled, read response with optional retry
        if read_response:   
            return self.read_response(processing_seconds, num_response_bytes, retry=read_retry)
        else:
            return None, Error(None)
        

    def read_response(self, processing_seconds: float, num_response_bytes: int, 
        retry: bool = True) -> Tuple[Optional[str], Error]:
        """ Reads response from from device. Waits processing seconds then 
            tries to read num response bytes with optional retry. Returns 
            response string on success or raises exception on error. """

        # Give device time to process
        self.logger.debug("Waiting for {} seconds".format(processing_seconds))
        time.sleep(processing_seconds)

        # Read device data and parse response code
        self.logger.debug("Reading response")
        data, error = self.i2c.read(num_response_bytes) 

        # Check for errors
        if error.exists():
            error.report("Driver unable to read response")
            return None, error

        # Format response code
        response_code = int(data[0])

        # Check for invalid syntax
        if response_code == 2: 
            error = Error("Driver unable to read response, invalid command string syntax")
            return None, error

         # Check if still processing
        elif response_code == 254:

            # Try to read one more time if retry enabled
            if retry == True:
                self.logger.warning("Sensor did not finish processing in allotted time, retrying read")
                return self.read_response(processing_seconds, num_response_bytes, retry=False)
            else:
                error = Error("Driver unable to read response, insufficient processing time")
                return None, error
        
        # Check if device has no data to send
        elif response_code == 255: 

            # Try to read one more time if retry enabled
            if retry == True:
                self.logger.warning("Sensor reported no data to read, retrying read")
                return self.read_response(processing_seconds, num_response_bytes, retry=False)
            else:
                error = Error("Driver unable to read response, device has no data to send")
                return None, error

        # Invalid response code
        elif response_code != 1:
            error = Error("Driver unable to read response, invalid response code")
            return None, error

        # Successfully read response!
        response_message = data[1:].decode('utf-8').strip("\x00")
        self.logger.debug("Response:`{}`".format(response_message))
        return response_message, Error(None)


    def enable_protocol_lock(self) -> Error:
        """ Commands sensor to enable protocol lock. """
        self.logger.debug("Enabling protocol lock in hardware")

        # Send command
        _, error = self.process_command("Plock,1", processing_seconds=0.6) # was 0.3

        # Check for errors
        if error.exists():
            error.report("Driver unable to enable protocol lock")
            return error

        # Successfully enabled protocol lock!
        return Error(None)


    def disable_protocol_lock_disable(self) -> Error:
        """ Commands sensor to disable protocol lock. """
        self.logger.debug("Disabling protocol lock in hardware")

        # Send command
        _, error = self.process_command("Plock,0", processing_seconds=0.6) # was 0.3

        # Check for errors
        if error.exists():
            error.report("Driver unable to disable protocol lock")
            return error

        # Successfully disabled protocol lock!
        return Error(None)


    def enable_led(self) -> Error:
        """ Commands sensor to enable led. """
        self.logger.debug("Enabling led in hardware")

        # Send command
        _, error = self.process_command("L,1", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to enable led")
            return error

        # Successfully enabled led!
        return Error(None)


    def disable_led(self) -> Error:
        """ Commands sensor to disable led. """
        self.logger.debug("Enabling led in hardware")

        # Send command
        _, error = self.process_command("L,0", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to disable led")
            return error
        
        # Successfully disabled led! 
        return Error(None)


    def enable_sleep_mode(self) -> Error:
        """ Commands sensor to enter sleep mode. Note: Sensor will wake up by
            sending any command to it. """
        self.logger.debug("Enabling sleep mode in hardware")

        # Send command
        _, error = self.process_command("Sleep", processing_seconds=0.3, read_response=False)

        # Check for errors
        if error.exists():
            error.report("Driver unable to enable sleep mode")
            return error
        
        # Successfully enabled sleep mode!
        return Error(None)


    def read_status(self) -> Tuple[Dict, Error]:
        """ Reads status from device. """
        self.logger.debug("Reading status from hardware")

        # Send read status command to hardware
        response_message, error = self.process_command("Status", processing_seconds=0.3)

        # Check for errors
        if error.exists():
            error.report("Driver unable to read status")
            return None, error

        # Check for empty response message
        if response_message == None:
            error = Error("Driver unable to read status, received empty response message")
            return None, error

        # Parse response message
        command, code, voltage = response_message.split(",")
        self.logger.debug("Current voltage: {}V".format(voltage))

        # Break out restart code
        if code == "P":
            prev_restart_reason = "Powered off"
            self.logger.debug("Device previous restart due to powered off")
        elif code == "S":
            prev_restart_reason = "Software reset"
            self.logger.debug("Device previous restart due to software reset")
        elif code == "B":
            prev_restart_reason = "Browned out"
            self.logger.critical("Device browned out on previous restart")
        elif code == "W":
            prev_restart_reason = "Watchdog"
            self.logger.debug("Device previous restart due to watchdog")
        elif code == "U":
            self.prev_restart_reason = "Unknown"
            self.logger.warning("Device previous restart due to unknown")

        # Build status dict
        status = {
            "prev_restart_reason": prev_restart_reason,
            "voltage": voltage
        }

        # Successfully read status!
        return status, error
