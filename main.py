# Import state machine
from device.device import Device

# Setup logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




# Run main
if __name__ == "__main__":
	device = Device()
	device.run_state_machine()