# Import standard python modules
import os, time, socket, struct, json

# Import python types
from typing import Tuple, Dict, Any, List

""" Notes from docs/iHP Communications Protocol  Definitions (Rev0.1).pdf

p.65 reading DIRECT data:
    Module PMBUS Command 8Bh (READ_VOUT)
    number of bytes = 3 
    Multiplier = N = 10000
    Command returns data of 0757B0h Converted to decimal = 481200
    Y = X * N 
    481200 = X * 10000
    X = 48.12 V

UDP packet format:

bytes of a COMMAND message: p.5
1-4     4 bytes message ID (I generate a sequential one).
  5     A1h (constant, except for ping which is A0h).
  6     000 + (low 5 bits internal device address) 00h=COMMS, mod1-8=10h-17h
  7     READ 01 + (low 6 bits for data length starting at 9th byte)
        WRITE 00 + (low 6 bits for data length starting at 9th byte)
  8     1 byte command code:  
            p.27 for module, p.44 for data sizes.
            p 47 for isocomm (all modules?), p.60 data sizes.
  9     Zero to N data bytes.

bytes of a RESPONSE message:  p.7
1-4     4 bytes message ID (matches what is sent in command)
  5     -0-- first nibble success
        -1-- first nibble error
        ---1 second nibble, message has response
        ---0 second nibble, message is blank
  6     0000 ---- normal, or error code in first nibble
  7     ---X XXXX device address
  8     --LL LLLL resonse data len
  9     1 byte command code
10+     response data bytes

EVERY message sent will be responded to (if valid and to active device).

p.20 error codes.


"""


class Messaging:
    def __init__(
        self,
        config_file: str = None,
        simulate: bool = False,
        debug: bool = False
    ) -> None:
        self.config_file = config_file
        self.simulate = simulate
        self.debug = debug
        self.UDP_message_ID = 1

        # load our artesyn message config
        self.config = json.load(open(self.config_file, 'r'))
        self.name = self.config.get('name')
        print(f"loaded {self.name}")
        self.brain_IP = self.config.get('config', {}).get('brain_IP')
        self.module_IPs = self.config.get('config', {}).get('module_IPs', [])
        if self.simulate:
            self.brain_IP = "127.0.0.1"
            self.module_IPs.append(self.brain_IP)
        self.slot_addresses = self.config.get('config', {}).get('slot_addresses', [])
        self.UDP_port = self.config.get('config', {}).get('UDP_port', 8888)
        self.UDP_messages = self.config.get('UDP_messages', {})
        self.commands = self.config.get('commands', {})

        # create our socket for bi-directional UDP messaging
        self.sock = socket.socket(socket.AF_INET,    # Internet
                                  socket.SOCK_DGRAM) # UDP
        self.sock.bind((self.brain_IP, self.UDP_port)) # for receiving response
        self.sock.settimeout(0.2) # seconds


    def get_module_IPs(self) -> List[str]:
        return self.module_IPs


    def get_commands(self) -> List[str]:
        return self.commands.keys()


    def send(self, command: str, 
                   IP: str, 
                   slot: int = 0, 
                   value: int = 0, 
                   port: int = None) -> None:
        """ Send a command and wait a short time for a response.
        """
        if command not in self.commands:
            print(f"Error: command {command} not found in {self.get_commands()}")
            return
        if IP not in self.module_IPs:
            print(f"Error: IP {IP} not found in {self.module_IPs}")
            return
        if slot < 0 or slot >= len(self.slot_addresses):
            print(f"Error: slot {slot} out of range: 0 to {len(self.slot_addresses)}")
            return
        if value < 0 or value > 100:
            print(f"Error: value {value} out of range: 0 to 100 percent")
            return
        if port is None:
            port = self.UDP_port
        cmd = self.commands.get(command, {})
        msgs = cmd.get('UDP_messages', [])
        for msg in msgs:
            print(f"{command} sending message {msg}")
            msg_id = self.__send(msg, IP, slot, value, port)
            error, value = self.__get_response(msg_id)
#TBD: do something with response


    def __send(self, message: str, IP: str, slot: int, value: int, port: int) -> bytes:
        """ Send the UDP message, return the message ID.
        """
        if message not in self.UDP_messages:
            print(f"Error: {message} not in {self.UDP_messages.keys()}")
            return
        msg_id = struct.pack(">i", self.UDP_message_ID)
        self.UDP_message_ID += 1
        msg = self.UDP_messages.get(message, {})

        # build up the data part of the UDP packet
        data = msg_id # bytes 1 to 4, message ID
        
        # 5th byte, num commands (zero or one)
        data += bytes.fromhex(msg.get('5', 'A0')) 

        # handle messages that address a slot directly
        device_address = msg.get('6_device_address', '00') # 6th byte
        if message == "READ_SLOT_VOUT" or \
           message == "READ_SLOT_IOUT" or \
           message == "WRITE_SLOT_IREF":
            device_address = self.slot_addresses[slot]
        # 6th byte, device address (module or slot)
        data += bytes.fromhex(device_address) 

        # 7th byte, read or write and command data length
        data += bytes.fromhex(msg.get('7_read_or_write_and_data_length', '00'))

        # 8th byte, command code (optional for ping)
        command_code = msg.get('8_command_code')
        if command_code is not None:
            data += bytes.fromhex(command_code)

        # this command writes two bytes of data (the only one)
        if message == "WRITE_SLOT_DIGITAL_CURRENT_SOURCE_MODE":
            slots = msg.get('9_module_slots', [])
            data += bytes.fromhex(slots[slot])

        # 9th byte, data (optional for ping)
        nine_data = msg.get('9_data', '')
        if nine_data is not None:
            data += bytes.fromhex(nine_data)

        # the 9-11th bytes (three) for this command is the percentage x10000
        if message == "WRITE_SLOT_IREF":
            if 0 == value:
                val_in_hex_str = '000000'
            else:
                val_in_hex_str = hex(value*10000)[2:] 
                if 4 == len(val_in_hex_str):
                    val_in_hex_str = '00' + val_in_hex_str
                elif 5 == len(val_in_hex_str):
                    val_in_hex_str = '0' + val_in_hex_str
            data += bytes.fromhex(val_in_hex_str)

        print(f"sending:\n\t{data}")
        self.sock.sendto(data, (IP, port))
        time.sleep(msg.get('delay_secs', 0.02))
        return msg_id


    def __get_response(self, message_ID: int) -> Tuple[str, float]:
        """ return the error string (if any) and value (if any)
        """
        data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
        print(f"response:\n\t{data}")
        return "", 0
#TBD: parse error code, return data


