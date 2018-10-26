# Import standard python modules
import datetime, jwt

# Import python types
from typing import NamedTuple, Any

# Import device utilities
from device.utilities.logger import Logger

# Initialize logger
logger = Logger("IotTokenUtility", "iot")


class JsonWebToken(NamedTuple):
    """Dataclass for json web token."""

    encoded: Any  # TODO: Get type
    issued_timestamp: float
    expiration_timestamp: float

    @property
    def is_expired(self) -> bool:
        """Checks if token is expired."""
        current_timestamp = datetime.datetime.utcnow().timestamp()
        return current_timestamp > self.expiration_timestamp


def create_json_web_token(
    project_id: str,
    private_key_filepath: str,
    encryption_algorithm: str = "RS256",
    time_to_live_minutes: int = 60,
) -> JsonWebToken:
    """Creates a json web token."""
    logger.debug("Creating json web token")

    # Initialize token variables
    issued_timestamp = datetime.datetime.utcnow().timestamp()
    time_delta = datetime.timedelta(minutes=time_to_live_minutes).seconds
    expiration_timestamp = issued_timestamp + time_delta

    # Build token
    token = {"iat": issued_timestamp, "exp": expiration_timestamp, "aud": project_id}

    # Load private key and encode token
    try:
        with open(private_key_filepath, "r") as f:
            private_key = f.read()
        encoded_jwt = jwt.encode(token, private_key, algorithm=encryption_algorithm)
    except FileNotFoundError:
        message = "Unable to create token, private key file not found"
        logger.warning(message)
        raise ValueError(message)
    except NotImplementedError:
        message = "Unable to create token, invalid encryption algorithm"
        logger.error(message)
        raise ValueError(message)
    except Exception as e:
        msg = "Unable to create token, unhandled exception: {}".format(type(e))
        logger.exception(msg)
        raise

    # Build json web token object
    json_web_token = JsonWebToken(
        encoded=encoded_jwt,
        issued_timestamp=issued_timestamp,
        expiration_timestamp=expiration_timestamp,
    )

    # Successfully created json web token
    return json_web_token
