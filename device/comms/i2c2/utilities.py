import struct, inspect, threading
from ctypes import *


class i2c_msg(Structure):
    _fields_ = [
        ("addr", c_uint16),
        ("flags", c_uint16),
        ("len", c_uint16),
        ("buf", POINTER(c_uint8)),
    ]


class i2c_rdwr_ioctl_data(Structure):
    _fields_ = [("msgs", POINTER(i2c_msg)), ("nmsgs", c_uint32)]


def make_i2c_rdwr_data(messages):  # type: ignore
    """Utility function to create and return an i2c_rdwr_ioctl_data structure
    populated with a list of specified I2C messages.  The messages parameter
    should be a list of tuples which represent the individual I2C messages to
    send in this transaction.  Tuples should contain 4 elements: address value,
    flags value, buffer length, ctypes c_uint8 pointer to buffer.
    """
    # Create message array and populate with provided data.
    msg_data_type = i2c_msg * len(messages)
    msg_data = msg_data_type()
    for i, m in enumerate(messages):
        msg_data[i].addr = m[0] & 0x7F
        msg_data[i].flags = m[1]
        msg_data[i].len = m[2]
        msg_data[i].buf = m[3]
    # Now build the data structure.
    data = i2c_rdwr_ioctl_data()
    data.msgs = msg_data
    data.nmsgs = len(messages)
    return data
