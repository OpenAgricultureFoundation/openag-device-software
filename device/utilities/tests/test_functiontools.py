# Import standard python libraries
import os, sys, pytest, logging

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import device utilities
from device.utilities.logger import Logger

# Import functiontools
from device.utilities.functiontools import retry

logging.basicConfig(level=logging.DEBUG)


# class ExampleClass(object):

#     def __init__(self) -> None:
#         self.logger = Logger(name="ExampleClass", dunder_name=__name__)
#         self.logger.debug("Initializing communication")

#     @retry(ZeroDivisionError, tries=5, delay=0.2, backoff=3)
#     def foo(self, retry: bool = True) -> None:
#         self.logger.debug("foo")
#         1 / 0


# def test_retry() -> None:
#     e = ExampleClass()
#     e.foo()
#     assert False
