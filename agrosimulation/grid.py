

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
        # functions that belong to each parameter
        self.functions = None

    def setProperties(self, generator):
        properties = []
        properties.append(generator._max_volume[0:-1])
        properties.append(generator._max_time[0:-1])
        properties.append(generator._pregnant_volume[0:-1])
        properties.append(generator._lactant_time[0:-1])
        properties.append(generator._dry_time[0:-1])
        properties.append(generator._pregnant_time[0:-1])
        self.properties = properties

    def setFunctions(self, generator):
        functions = []
        functions.append(generator._distributions[generator._max_volume[-1]])
        functions.append(generator._distributions[generator._max_time[-1]])
        functions.append(generator._distributions[generator._pregnant_volume[-1]])
        functions.append(generator._distributions[generator._lactant_time[-1]])
        functions.append(generator._distributions[generator._dry_time[-1]])
        functions.append(generator._distributions[generator._pregnant_time[-1]])
        self.functions = functions
