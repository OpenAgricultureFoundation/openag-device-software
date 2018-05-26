# Import python modules
import logging, time, threading, os, sys, datetime, json, sys, traceback, copy

# Import the IoT communications class
from iot.iot_pubsub import IoTPubSub

"""
Jake:
So i see 2 cases. The first is state which we want updated as fast as possible
as frequently as possible, however to start i might just send all state every
second to a cloud table that removes the old entry of state each time it
receives a new one so there is only ever one instance of state in the table.
That is what Manu will poll to get the most up to date device information.

Then, the second one is environment history which is stored forever but
infrequently updated (e.g. every few minutes). For this I think it makes the
most sense to read directly from the environment table that already exists and
send payloads the cloud. Upon payload receive confirmation, turn the
'is_synced' flag in the database ON.

There is also the new events case (e.g. start a recipe, etc) that we need to
figure out.  

debugrob
What if I send the entire state on first connection (and save it), then each
minute look for diffs and just send the diffs?

Should I write that to a local table then have this thread pick it up and send
it?

"""


class IoTManager:
    """ Manages IoT communications to the Google cloud backend MQTT service """

    # Initialize logger
    extra = {"console_name":"IoT", "file_name": "IoT"}
    logger = logging.getLogger( 'iot' )
    logger = logging.LoggerAdapter(logger, extra)

    # Place holder for thread object.
    thread = None

    # Keep track of the previous values that we have published.  
    # We only publish a value if it changes.
    prev_vars = None

    def __init__(self, state):
        """ Class constructor """
        self.state = state
        self.error = None
        self._stop_event = threading.Event() # so we can stop this thread
        try:
            self.iot = IoTPubSub() 
        except( Exception ) as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.logger.critical( "Exception creating class: {}".format( e ))
            traceback.print_tb( exc_traceback, file=sys.stdout )
            exit( 1 )


    @property
    def error(self):
        """ Gets error value. """
        return self._error


    @error.setter
    def error(self, value):
        """ Safely updates recipe error in shared state. """
        self._error= value
#debugrob: need iot dict in state if we do this
#        with threading.Lock():
#            self.state.iot["error"] = value


    def spawn(self):
        self.logger.info("Spawing IoT thread")
        self.thread = threading.Thread( target=self.thread_proc )
        self.thread.daemon = True
        self.thread.start()


    def stop(self):
        self.logger.info("Stopping IoT thread")
        self._stop_event.set()


    def stopped(self):
        return self._stop_event.is_set()


    def publish( self ):
        vars_dict = self.state.environment["reported_sensor_stats"] \
            ["individual"]["instantaneous"]

        # Keep a copy of the first set of values (usually None).
        if self.prev_vars == None:
            self.prev_vars = copy.deepcopy( vars_dict )

        # for each value, only publish the ones that have changed.
        for var in vars_dict:
            if self.prev_vars[var] != vars_dict[var]:
                self.prev_vars[var] = copy.deepcopy( vars_dict[var] )
                self.iot.publishEnvVar( var, vars_dict[var] )

        """
#debugrob: later:
    self.iot.publishCommandReply( commandName, valuesJsonString )
        """

    def thread_proc( self ):
        while True:
            if self.stopped():
                break
            # send and receive messages over IoT
            self.iot.process_network_events() 
            time.sleep( 0.1 )



