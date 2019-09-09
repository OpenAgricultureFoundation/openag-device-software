# Communicate over BACnet by wrapping the bacpypes module to do the real work.
# https://bacpypes.readthedocs.io/en/latest

import os, socket    

from bacpypes.apdu import WhoIsRequest
from bacpypes.app import BIPSimpleApplication
from bacpypes.consolelogging import ConfigArgumentParser
from bacpypes.core import deferred, enable_sleeping
from bacpypes.debugging import bacpypes_debugging
from bacpypes.iocb import IOCB
from bacpypes.local.device import LocalDeviceObject
from bacpypes.pdu import Address, GlobalBroadcast

#debugrob: add code from samples/ReadWriteProperty.py 
# (after getting property names from ReadAllProperties.py)
from bacpypes.object import get_datatype, get_object_class
from bacpypes.apdu import SimpleAckPDU, \
    ReadPropertyRequest, ReadPropertyACK, WritePropertyRequest
from bacpypes.primitivedata import Null, Atomic, Boolean, Unsigned, Integer, \
    Real, Double, OctetString, CharacterString, BitString, Date, Time, \
    ObjectIdentifier
from bacpypes.constructeddata import Array, Any, AnyAtomic

from device.utilities.logger import Logger
from device.peripherals.modules.bacnet import bnet_base

# bacpypes debugging
_debug = 1


#------------------------------------------------------------------------------
@bacpypes_debugging
class Bnet(bnet_base.BnetBase):

    def __init__(self, 
                 logger: Logger, 
                 ini_file: str = None, 
                 debug: bool = False
                 ) -> None:
        path = os.path.dirname(bnet_base.__file__)
        self.ini_file = path + '/' + ini_file
        self.debug = debug
        self.logger = logger
        self.logger.debug(f"init: bacpypes with {self.ini_file}")
        self.reset() # read config, set up the app
        enable_sleeping() # for bacpypes threading


    def setup(self) -> None:
        self.logger.debug("setup")


    def reset(self) -> None:
        self.logger.debug("resetting...")
        cmd_line_args_simulated = []
        if self.debug:
            cmd_line_args_simulated.append("--debug")
            cmd_line_args_simulated.append(__name__)
        cmd_line_args_simulated.append("--ini")
        cmd_line_args_simulated.append(self.ini_file)
        self.args = ConfigArgumentParser().parse_args(cmd_line_args_simulated)

        # make a device object
        self.device = LocalDeviceObject(ini=self.args.ini) 

        # Overwrite the IP address in the .ini file to match what this machine
        # is configured for (to work, it must be a static IP on the same
        # subnet as the reliable / bacnet devices: 192.168.1.XXX/24
        self.IP = socket.gethostbyname(socket.gethostname()) + "/24"
        self.args.ini.address = self.IP
        self.logger.debug(f"init: IP {self.IP}")

        # make an application to get callbacks from bacpypes
        self.app = App(self.logger, self.device, self.args.ini.address)


    def ping(self) -> None:
        try:
            # build a request
            request = WhoIsRequest() 
            # ping all devices on network
            request.pduDestination = GlobalBroadcast() 
            # make an IOCB (input output callback)
            iocb = IOCB(request)
            # give it to the application to handle the ASYNC request
            self.app.request_io(iocb)
        except Exception as err:
            self.logger.critical(err)

    def set_test_voltage(self, voltage: float) -> None:
        try:
            self.logger.info(f"set_test_voltage {voltage} for port {self.args.ini.test_voltage_port}")

            # write <addr> <objid> <prop> <value> 
            addr = self.args.ini.send_commands_to_object_id
            obj_id = self.args.ini.test_voltage_port
            prop_id = self.args.ini.test_voltage_prop_id
            self.logger.debug(f"debugrob from ini obj_id {obj_id}")

#debugrob: TBD, guessing at prop id (it's in the ini file)
# 'analogOutput' is an OBJECT TYPE
# in basetypes.py PropertyIdentifier: setpoint, valueSet, volts,  ?

            obj_id = ('analogOutput', 1001) # debugrob, obj_type, device id?
            obj_id = ObjectIdentifier(obj_id).value
            self.logger.debug(f"debugrob value obj_id={str(obj_id)}")

            prop_id = 'valueSet' #debugrob, can also try setpoint and volts

            cls = get_object_class(obj_id)
            if cls:
                self.logger.debug(f"debugrob properties for obj_id={cls._properties}")
            datatype = get_datatype(obj_id, prop_id)
            self.logger.debug(f"debugrob datatype={datatype}")

            value = float(voltage)
            self.logger.debug(f"debugrob value={value}")

            request = WritePropertyRequest(
                objectIdentifier=obj_id,
                propertyIdentifier=prop_id
                )
            request.pduDestination = Address(addr)

            request.propertyValue = Any()
            try:
                request.propertyValue.cast_in(value)
            except Exception as err:
                self.logger.critical(err)

            iocb = IOCB(request)

            # give it to the application
            deferred(this_application.request_io, iocb)

            # wait for it to complete
            self.logger.debug(f"debugrob waiting for iocb...")
            iocb.wait()

            # do something for success
            if iocb.ioResponse:
                apdu = iocb.ioResponse

                # should be an ack
                if not isinstance(apdu, ReadPropertyACK):
                    self.logger.error(f"response: Not an ACK")
                    return

                # find the datatype
                datatype = get_datatype(apdu.objectIdentifier[0], 
                        apdu.propertyIdentifier)
                self.logger.debug(f"response: datatype {datatype}")
                if not datatype:
                    self.logger.error(f"response: unknown datatype")
                    return

                value = apdu.propertyValue.cast_out(datatype)
                self.logger.debug(f"response: value {value}")

                if hasattr(value, 'debug_contents'):
                    value.debug_contents(file=sys.stdout)
                    sys.stdout.flush()

            # do something for error/reject/abort
            if iocb.ioError:
                self.logger.error(f"response: {str(iocb.ioError)}")

        except Exception as err:
            self.logger.critical(err)

    def set_air_temp(self, tempC: float) -> None:
        self.logger.info(f"set_air_temp {tempC}")
#debugrob: TBD after figuring out property names using interactive sample

    def set_air_RH(self, RH: float) -> None:
        self.logger.info(f"set_air_RH {RH}")
#debugrob: TBD after figuring out property names using interactive sample


#------------------------------------------------------------------------------
@bacpypes_debugging
class App(BIPSimpleApplication):
    def __init__(self, logger: Logger, *args):
        BIPSimpleApplication.__init__(self, *args)
        self.logger = logger

        # keep track of requests to line up responses
        self._request = None

    def request(self, apdu):
        self.logger.debug(f"App request {apdu.dict_contents()}")

        # save a copy of the request
        self._request = apdu

        # forward it along
        BIPSimpleApplication.request(self, apdu)

    def confirmation(self, apdu):
        self.logger.debug(f"App confirmation {apdu.dict_contents()}")

        # forward it along
        BIPSimpleApplication.confirmation(self, apdu)

    def indication(self, apdu):
        self.logger.debug(f"App indication {apdu.dict_contents()}")

        if (isinstance(self._request, WhoIsRequest)) and (isinstance(apdu, IAmRequest)):
            device_type, device_instance = apdu.iAmDeviceIdentifier
            if device_type != 'device':
                raise DecodingError("invalid object type")

            if (self._request.deviceInstanceRangeLowLimit is not None) and \
                    (device_instance < self._request.deviceInstanceRangeLowLimit):
                pass
            elif (self._request.deviceInstanceRangeHighLimit is not None) and \
                    (device_instance > self._request.deviceInstanceRangeHighLimit):
                pass
            else:
                # print out the contents
                self.logger.info(f"App pduSource={repr(apdu.pduSource)}")
                self.logger.info(f"App iAmDeviceIdentifier={str(apdu.iAmDeviceIdentifier)}")

        # forward it along
        BIPSimpleApplication.indication(self, apdu)


