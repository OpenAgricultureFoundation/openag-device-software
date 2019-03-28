import os
from device.utilities.network.base_network_utility import NetworkUtility
from device.utilities.network.generic_network_utility import GenericNetworkUtility


class NetworkUtilityFactory:
    """Factory class with static method to get appropriate NetworkUtility implementation"""

    @staticmethod
    def get_network_utils() -> NetworkUtility:
        """Get the NetworkUtility implementation for the platform"""
        if os.getenv(
            "BALENA"
        ):  # This is true when running on a Balena enabled platform
            from device.utilities.network.balena_network_utility import (
                BalenaNetworkUtility,
            )

            return BalenaNetworkUtility()

        return GenericNetworkUtility()
