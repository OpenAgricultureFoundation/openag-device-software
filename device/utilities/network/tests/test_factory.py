import pytest
from device.utilities.network.network_utility_factory import (
    NetworkUtilityFactory as Factory,
)
from device.utilities.network.generic_network_utility import GenericNetworkUtility

# TODO: figure out how to deal with NetworkManager not exisiting in non-Balena environments
#   then test getting a BalenaNetworkUtility


def test_get_generic_network_utility() -> None:
    gnu = Factory.get_network_utils()
    assert isinstance(gnu, GenericNetworkUtility)
