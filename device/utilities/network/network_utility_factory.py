import os
from device.utilities.network.base_network_utility import NetworkUtility
from device.utilities.network.generic_network_utility import GenericNetworkUtility
from device.utilities.network.balena_network_utility import BalenaNetworkUtility


class NetworkUtilityFactory:

    @staticmethod
    def get_network_utils() -> NetworkUtility:
        if os.getenv("BALENA"):  # This is true when running on a Balena enabled platform
            return BalenaNetworkUtility()
        return GenericNetworkUtility()
