# Import standard python modules
from typing import List


class Health:
    """ Manages health of an entity by receiving success or failure updates 
        then calculates health percent based off previously queued readings. """

    def __init__(self, updates: int = 5, minimum: float = 60.0) -> None:
        """ Initialized health, sets number of updates stored in queue and 
            minimum health required to report healthy. """
        self.updates = updates
        self.minimum = minimum
        self.percent = 100.0
        self.queue: List[float] = []


    def __str__(self) -> str:
        return "Health(healthy={}, percent={}, minimum={}, updates={})".format(
                self.healthy, self.percent, self.minimum, self.updates)


    def report_success(self) -> None:
        """ Reports sucessful update. """
        self.update(successful=True)


    def report_failure(self) -> None:
        """ Reports failed update. """
        self.update(successful=False)


    def update(self, successful: bool) -> None:
        """ Updates health. """

        # Increment successes/failures count
        if successful:
            self.queue.append(1.0)
        else:
            self.queue.append(0.0)

        # Trim queue if longer than updates
        if len(self.queue) > self.updates:
            self.queue.pop(0)

        # Calculate health percent
        self.percent = sum(self.queue) / len(self.queue) * 100.0


    def reset(self) -> None:
        """ Resets health. """
        self.percent = 100.0
        self.queue = []


    @property
    def healthy(self) -> bool:
        """ Check if process is healthy. Requires minimum updates before
            will report unhealthy. Determines unhealthy if health percent
            drops below minimum percent. """

        # Check for minimum updates
        if len(self.queue) < self.updates:
            return True

        # Check health percent >= minimum health
        if self.percent < self.minimum:
            return False
        else:
            return True
