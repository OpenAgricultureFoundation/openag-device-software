# Import standard python modules
import datetime, jwt

# Import device utilities
from device.utilities.logger import Logger

# Initialize logger
logger = Logger("IotTokenUtility")


class JsonWebToken(NamedTuple):
    """Dataclass for json web token."""
    encoded: Any  # TODO: Get type
    issued_timestamp: float
    expiration_timestamp: float

    @property
    def is_expired(self):
        """Checks if token is expired."""
        current_timestamp = datetime.datetime.utcnow().timestamp()
        return current_timestamp > self.expiration_timestamp


def create_json_web_token(
    self,
    project_id: str,
    private_key_filepath: str,
    encryption_algorithm: str = "RSA256",
    time_to_live_minutes: int = 60,
) -> JsonWebToken:
    """Creates a json web token."""
    self.logger.debug("Creating json web token")

    # Initialize token variables
    issued_timestamp = datetime.datetime.utcnow().timestamp()
    time_delta = datetime.timedelta(minutes=time_to_live_minutes).seconds
    expiration_timestamp = issued_timestamp + time_delta

    # Build token
    token = {"iat": issued_timestamp, "exp": expiration_timestamp, "aud": project_id}

    # Load private key
    try:
        with open(private_key_filepath, "r") as f:
            private_key = f.read()
    except Exception as e:
        message = "Unable to create json web token, unable to load private key, unhandled exception: {}".format(
            type(e)
        )
        self.logger.exception(message)
        raise

    # Encode token
    encoded_jwt = jwt.encode(token, private_key, algorithm=encryption_algorithm)

    # Build json web token object
    json_web_token = JsonWebToken(
        encoded=encoded_jwt,
        issued_timestamp=issued_timestamp,
        expiration_timestamp=expiration_timestamp,
    )

    # Successfully encoded json web token
    return json_web_token
