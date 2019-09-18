# Communicate over BACnet by wrapping the bacpypes module to do the real work.
# https://bacpypes.readthedocs.io/en/latest

import os, socket, json, time, asyncore    

from typing import Dict

from bacpypes.apdu import WhoIsRequest, SimpleAckPDU, \
    ReadPropertyRequest, ReadPropertyACK, WritePropertyRequest
from bacpypes.app import BIPSimpleApplication
from bacpypes.consolelogging import ConfigArgumentParser
from bacpypes.core import run_once 
from bacpypes.debugging import bacpypes_debugging
from bacpypes.iocb import IOCB
from bacpypes.local.device import LocalDeviceObject
from bacpypes.pdu import Address, GlobalBroadcast
from bacpypes.object import get_datatype, get_object_class
from bacpypes.primitivedata import ObjectIdentifier
from bacpypes.constructeddata import Any
from bacpypes.task import TaskManager

from device.utilities.logger import Logger
from device.peripherals.modules.bacnet import bnet_base

# bacpypes debugging, set this to 0 to turn off
_debug = 1


#------------------------------------------------------------------------------
@bacpypes_debugging
class Bnet(bnet_base.BnetBase):

    def __init__(self, 
                 logger: Logger, 
                 ini_file: str = None, 
                 config_file: str = None,
                 debug: bool = False
                 ) -> None:
        path = os.path.dirname(bnet_base.__file__)
        self.ini_file = path + '/' + ini_file
        self.config_file = path + '/' + config_file
        self.debug = debug
        self.logger = logger
        self.logger.debug(f"init: bacpypes with {self.ini_file}")

        cmd_line_args_simulated = []
        if self.debug:
            cmd_line_args_simulated.append("--debug")
            cmd_line_args_simulated.append(__name__)
        cmd_line_args_simulated.append("--ini")
        cmd_line_args_simulated.append(self.ini_file)
        self.args = ConfigArgumentParser().parse_args(cmd_line_args_simulated)

        # load our reliable config file that has ports, names, types, etc.
        self.bacnet_config = json.load(open(self.config_file, 'r'))
        self.logger.debug(f"loaded {self.bacnet_config.get('name')}")
        
        # make a device object
        self.device = LocalDeviceObject(ini=self.args.ini) 

        # Overwrite the IP address in the .ini file to match what this machine
        # is configured for (to work, it must be a static IP on the same
        # subnet as the reliable / bacnet devices: 192.168.1.XXX/24
        self.logger.debug(f"init: IP {self.args.ini.address}")

        # make an application to get callbacks from bacpypes
        self.app = BIPSimpleApplication(self.device, self.args.ini.address)
        self.taskman = TaskManager()


    def setup(self) -> None:
        self.logger.debug("setup")


    def reset(self) -> None:
        self.logger.debug("resetting...")


    # Get one of our bacnet config objs from out config dict
    def __get_object(self, obj_id: str) -> Dict:
        for obj in self.bacnet_config.get('objects'):
            if obj.get('id') == obj_id:
                return obj
        return {}

    def __get_device(self) -> str:
        return self.bacnet_config.get('config').get('device_master')

    def __get_prop(self) -> str:
        return self.bacnet_config.get('config').get('object_value_prop')

    # Ping all bacnet devices and write them to stdout
    def ping(self) -> None:
        try:
            # build a request
            request = WhoIsRequest() 
            # ping all devices on network
            request.pduDestination = GlobalBroadcast() 
            # make an IOCB (input output callback)
            iocb = IOCB(request)
            self.app.request_io(iocb)
            self.logger.debug("ping: waiting for responses...")
            loopCount = 0
            while loopCount < 10:
                loopCount += 1
                run_once()
                asyncore.loop(timeout=0.2, count=1)
                time.sleep(0.2)
                self.logger.debug(f"ping: loopy {loopCount}")
            self.logger.debug("ping: done with whois")
#debugrob: 

            # handle responses
            if iocb.ioResponse:
                self.logger.debug(f"ping: iocb response success!")
                apdu = iocb.ioResponse
                if not isinstance(apdu, IAmRequest):
                    self.logger.error(f"ping: Not an IAmRequest")
                    return
                device_type, device_instance = apdu.iAmDeviceIdentifier
                if device_type != 'device':
                    raise DecodingError("ping: invalid object type")
                self.logger.info(f"ping: pduSource={repr(apdu.pduSource)}")
                self.logger.info(f"ping: deviceId={str(apdu.iAmDeviceIdentifier)}")

            # do something for error/reject/abort
            if iocb.ioError:
                self.logger.error(f"ping: {str(iocb.ioError)}")

        except Exception as err:
            self.logger.critical(err)


    # Helper to read a value
    def __read_value(self, config_obj_id: str) -> float:
        try:
            # get config obj
            obj = self.__get_object(config_obj_id)
            obj_id = obj.get('object_id')
            obj_id = ObjectIdentifier(obj_id).value # make a bacpypes obj id
            addr = self.__get_device()
            prop_id = self.__get_prop()

            # read <addr> <objid> <prop> 
            self.logger.debug(f"read: {config_obj_id} for port \'{obj.get('name')}\' {addr} {str(obj_id)} {prop_id}")

            request = ReadPropertyRequest(
                objectIdentifier=obj_id,
                propertyIdentifier=prop_id
                )
            request.pduDestination = Address(addr)

            iocb = IOCB(request)
            self.app.request_io(iocb)
            self.logger.debug("read: waiting for response...")
            loopCount = 0
            while loopCount < 15:
                loopCount += 1
                run_once()
                asyncore.loop(timeout=0.2, count=1)
                time.sleep(0.2)
                self.logger.debug(f"read: loopy {loopCount}")
            self.logger.debug("read: done waiting")
#debugrob: not working, why?  it works in the reliable main tests

            # do something for success
            if iocb.ioResponse:
                self.logger.debug(f"read: iocb response success!")
                apdu = iocb.ioResponse

                # should be an ack
                if not isinstance(apdu, ReadPropertyACK):
                    self.logger.error(f"read: response: Not an ACK")
                    return 0

                # find the datatype
                datatype = get_datatype(apdu.objectIdentifier[0], 
                        apdu.propertyIdentifier)
                self.logger.debug(f"read: datatype {datatype}")
                if not datatype:
                    self.logger.error(f"read: unknown datatype")
                    return

                value = apdu.propertyValue.cast_out(datatype)
                self.logger.debug(f"read: value {value}")

                if hasattr(value, 'debug_contents'):
                    value.debug_contents(file=sys.stdout)
                    sys.stdout.flush()

                return value

            # do something for error/reject/abort
            if iocb.ioError:
                self.logger.error(f"read: ioError {str(iocb.ioError)}")

        except Exception as err:
            self.logger.critical(err)


    # Helper to write a value
    def __write_value(self, config_obj_id: str, _value: float) -> None:
        try:
            # get config obj
            obj = self.__get_object(config_obj_id)
            obj_id = obj.get('object_id')
            obj_id = ObjectIdentifier(obj_id).value # make a bacpypes obj id
            addr = self.__get_device()
            prop_id = self.__get_prop()

            # write <addr> <objid> <prop> <value> 
            value = float(_value)
            self.logger.debug(f"write: {config_obj_id} {_value} for port \'{obj.get('name')}\' {str(obj_id)} {prop_id} {value}")

            request = WritePropertyRequest(
                objectIdentifier=obj_id,
                propertyIdentifier=prop_id
                )
            request.pduDestination = Address(addr)

            # the value to write 
            datatype = get_datatype(obj_id[0], prop_id)
            value = datatype(value)
            request.propertyValue = Any()
            try:
                request.propertyValue.cast_in(value)
            except Exception as err:
                self.logger.critical(err)

            iocb = IOCB(request)
            self.app.request_io(iocb)
            self.logger.debug("write: waiting for response...")
            loopCount = 0
            while loopCount < 5:
                loopCount += 1
                run_once()
                asyncore.loop(timeout=0.2, count=1)
                time.sleep(0.2)
                self.logger.debug(f"write: loopy {loopCount}")
            self.logger.debug("write: done waiting")
#debugrob: 

            # do something for success
            if iocb.ioResponse:
                self.logger.debug(f"write: iocb response success!")

                apdu = iocb.ioResponse

                # should be an ack
                if not isinstance(iocb.ioResponse, SimpleAckPDU):
                    self.logger.error(f"write: Not an ACK")
                    return
                self.logger.debug(f"write: received ACK")

            # do something for error/reject/abort
            if iocb.ioError:
                self.logger.error(f"write: ioError {str(iocb.ioError)}")

        except Exception as err:
            self.logger.critical(err)


    def set_test_voltage(self, voltage: float) -> None:
        self.logger.info(f"set_test_voltage {voltage}")
        self.__write_value('test_v', voltage)


    def set_air_temp(self, tempC: float) -> None:
        # convert C to F
        tempF = (tempC * (9/5)) + 32
        self.logger.info(f"set_air_temp {tempC}C > {tempF}F")
        self.__write_value('set_air_temp', tempF)


    def set_air_RH(self, RH: float) -> None:
        self.logger.info(f"set_air_RH {RH}")
        self.__write_value('set_air_rh', RH)


    def get_air_temp(self) -> float:
        tempF = self.__read_value('air_temp')
        if tempF is None:
            return None
        # convert F to C
        tempC = (tempF - 32) * (5/9)
        self.logger.info(f"get_air_temp {tempC}C")
        return tempC


    def get_air_RH(self) -> float:
        if RH is None:
            return None
        RH = self.__read_value('air_RH')
        self.logger.info(f"get_air_RH {RH}%")
        return RH


