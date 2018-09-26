import time, inspect, threading
from functools import wraps
from typing import Any, Callable, TypeVar, Tuple, cast, Type

FuncType = Callable[..., Any]
F = TypeVar("F", bound=FuncType)


def retry(
    exceptions: Any,
    tries: int = 5,
    delay: float = 0.1,
    backoff: float = 2,
    logger: Any = None,
) -> Any:
    """Retry calling the decorated function using an exponential backoff.
    Checks for retry kwarg and adheres to default or passed in value.

    Args:
        exceptions: The exception to check. may be a tuple of
            exceptions to check.
        tries: Number of times to try (not retry) before giving up.
        delay: Initial delay between retries in seconds.
        backoff: Backoff multiplier (e.g. value of 2 will double the delay
            each retry).
        logger: Logger to use. If None, print.
    """

    def deco_retry(f: F) -> F:
        @wraps(f)
        def f_retry(*args: Any, **kwargs: Any) -> Any:

            # Get retry value from kwargs if it exists
            retry = kwargs.get("retry", None)

            # Check if retry passed into kwargs
            if retry == None:

                # Get kwargs defaults if it exists
                argspec = inspect.getfullargspec(f)
                positional_count = len(argspec.args) - len(argspec.defaults)
                defaults = dict(zip(argspec.args[positional_count:], argspec.defaults))

                # Get retry default value
                retry = defaults.get("retry", None)

            # Check if retry disabled
            if retry == False:
                return f(*args, **kwargs)

            # Note: If retry kwarg is None, we are assuming that if the decorator
            # is present, we should retry by default.

            # Note: We are not checking for retry in *args

            # Run function with retries
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exceptions as e:

                    # Try to log exceptions
                    try:
                        msg = "{}, retrying in {:.1f} seconds...".format(e, mdelay)
                        self = args[0]
                        self.logger.warning(msg)
                    except:
                        print("No logger configured")
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff

            # Check for thread lock
            return f(*args, **kwargs)

        return cast(F, f_retry)  # true decorator

    return deco_retry
