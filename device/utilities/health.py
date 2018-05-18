class Health:
    """ Manages health of an entity by receiving success or failure updates 
        then calculates health percent based off previously queued readings. """

    def __init__(self, updates=20, minimum=80):
        """ Initialized health, sets number of updates stored in queue and 
            minimum health required to report healthy. """
        
        self.updates = updates
        self.minimum = minimum
        self.healthy = True
        self.percent = 100
        self.queue = []


    def __str__(self):
        return "Health(healthy={}, percent={}, minimum={}, updates={})".format(
                self.healthy, self.percent, self.minimum, self.updates)


    def report_success(self):
        """ Reports sucessful update. """
        self.update(successful=True)


    def report_failure(self):
        """ Reports failed update. """
        self.update(successful=False)


    def update(self, successful):
        """ Updates health. """

        # Increment successes/failures count
        if successful:
            self.queue.append(1)
        else:
            self.queue.append(0)

        # Trim queue if longer than updates
        if len(self.queue) > self.updates:
            self.queue.pop(0)

        # Calculate health percent
        self.percent = float(sum(self.queue)) / len(self.queue) * 100

        # Check if healthy
        if self.percent < self.minimum:
            self.healthy = False
        else:
            self.healthy = True