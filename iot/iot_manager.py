# Import python modules
import logging, time, threading, os, sys, datetime, json

#debugrob: use DB storage in place of config.json (see recipe.py for example)
# Import database models
from app.models import IoTConfigModel

# Import the IoT communications class
#from iot.iot_pubsub import IotPubSub
#debugrob: use above later.  first get this thread receiving data to publish and commands to process.


class IoTManager:
    """ Manages IoT communications to the Google cloud backend MQTT service """

    # Initialize logger
    extra = {"console_name":"IoT", "file_name": "IoT"}
    logger = logging.getLogger( 'iot' )
    logger = logging.LoggerAdapter(logger, extra)

    # place holder for thread object
    thread = None

    def __init__(self, state):
        """ Class constructort """
        self.state = state
        self.error = None
        self._stop_event = threading.Event() # so we can stop this thread


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


#    @property
#    def commanded_mode(self):
#        """ Gets commanded mode from shared state. """
#        if "commanded_mode" in self.state.recipe:
#            return self.state.recipe["commanded_mode"]
#        else:
#            return None
#
#    @commanded_mode.setter
#    def commanded_mode(self, value):
#        """ Safely updates commanded mode in shared state. """
#        with threading.Lock():
#            self.state.recipe["commanded_mode"] = value


    def spawn(self):
        self.logger.info("Spawing IoT thread")
        self.thread = threading.Thread( target=self.thread_proc )
        self.thread.daemon = True
        self.thread.start()
#debugrob: use this code to save IoT config message version
        """
        try:
            c = IoTConfigModel.objects.latest()
            c.lastConfigVersion = 1
            c.device_id = 'debugrob'
            c.save()
        except:
            IoTConfigModel.objects.create( lastConfigVersion = 1,
                                           device_id = 'debugrob' )
        """


    def stop(self):
        self.logger.info("Stopping IoT thread")
        self._stop_event.set()


    def stopped(self):
        return self._stop_event.is_set()


    def thread_proc(self):
#debugrob: what do I do here?
        while True:
            if self.stopped():
                break
            time.sleep(0.1)



