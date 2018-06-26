class Modes(object):
    """ State machine modes """

    INVALID = "INVALID"
    NONE = "NONE"
    INIT = "INIT"
    SETUP = "SETUP"
    NORMAL = "NORMAL"
    RESET = "RESET"
    ERROR = "ERROR"
    SHUTDOWN = "SHUTDOWN"

    CALIBRATE = "CALIBRATE"
    MANUAL = "MANUAL"

    CONFIG = "CONFIG"
    LOAD = "LOAD"
    START = "START"
    QUEUED = "QUEUED"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    STOP = "STOP"
    NORECIPE = "NORECIPE"
