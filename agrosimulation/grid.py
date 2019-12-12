

class SimulationGrid():

    def __init__(self, ID, cows):
        """
        ID: Land code (Finca)
        volume: Liters of milk of the Land
        cows: It is a array with cow objects in the land
        """
        self.ID = ID
        self.cows = cows
        self.properties = None

        self._initial_time_params = None
        self._actual_cycle = None
        self._max_cycles = None

    def setProperties(self, generator):
        properties = generator._rvs
        self.properties = properties

    def setControlParameters(self, generator):
        """
        Control parameters. i.e. Initial conditions  of the simulation, and Parameters
        possible to be manipulated

        This method is intended to initializise for all iterations in Monte Carlo
        simulation, becasuse avoid initialize generator in each iteration. So, these
        parameters wont modified
        """
        self._initial_time_params = generator._initial_time
        self._actual_cycle = generator._actual_cycle
        self._max_cycles = generator._max_cycles
