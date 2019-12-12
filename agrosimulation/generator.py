import json

import numpy as np

from cow import Cow

# class JSONData():
#     # This module can be transport to simulation.py to optimize this code
#     # and use this object like enter parameter of the function main.py in agrosimulation
#     def __init__(self,path):
#         self.path = path
#
#     @property
#     def dict_obj(self):
#         with open(self.path, 'r') as f:
#             data=f.read()
#         return json.loads(data)

"""
The next distributions are independent of the code and are used to stimate
the random variables
"""
def _normalAtributes(param):
    value =  np.random.normal(param[0], param[1])
    return value

def _expAtributes(param):
    value =  np.random.exponential(1/param[0])
    return value

def _logisticAtributes(param):
    value =  np.random.logistic(param[0], param[1])
    return value

def _poissonAtributes(param):
    value =  np.random.poisson(param[0])
    return value

def _gamAtributes(param):
    value = np.random.gamma(param[0], param[1])
    return value

def _weibullAtributes(param):
    value = np.random.weibull(param[0])
    value = param[1]*value
    return value

class Generator():

    def __init__(self, path):
        """
        _RVS: Random Variables
        _distributions: bridge to name of distribution with the function
        _indexes: with this is not necessary to take  care of the order in agro.json
        """
        self.path = path

        self._distributions = { "EXPONENTIAL": _expAtributes,
                                "NORMAL": _normalAtributes,
                                "LOGISTIC": _logisticAtributes,
                                "POISSON": _poissonAtributes,
                                "GAMMA": _gamAtributes,
                                "WEIBULL": _weibullAtributes
                      }
        self._indexes = {
                            "EXPONENTIAL": {"lambda": 0},
                            "NORMAL": {"mean": 0, "std": 1},
                            "LOGISTIC": {"mean": 0, "scale": 1},
                            "POISSON": {"lambda": 0},
                            "GAMMA": {"shape": 0, "scale": 1},
                            "WEIBULL": {"shape": 0, "scale": 1}
        }
        # NOTE: lactant_time and dry time must be the penultimate and last in the list
        # of RVS, respectively
        self._RVS = {
            "CUADRATIC": ["dry-volume", "delta-Vo-Vd", "tL-tmax-ratio", "lactant-time", "dry-time"]
        }

        self._FEEDING = {
            "CORNELL-SIMPLIFIED": ["weight-of-cow", "reference-weight", "fat-percentage", "milk-density"]
        }
    """
    INIT: Control parameters. i.e. Initial conditions  of the simulation, and Parameters
    possible to be manipulated
    """
    @property
    def jsonData(self):
        with open(self.path, 'r') as f:
            data=f.read()
        return json.loads(data)

    @property
    def _n_of_cows(self):
        return self.jsonData["initial-conditions"]["cows"]["number"]

    @property
    def ID(self):
        return self.jsonData["grid-simulation"]["timeimp"]["ID"]

    @property
    def _simul_times(self):
        return np.array(self.jsonData["grid-simulation"]["timeimp"])

    @property
    def _max_cycles(self):
        options = self.jsonData["initial-conditions"]["cows"]["max-cycles"]
        if options["type"] == "CONS":
            value = options["values"]
            max_cycles = value*self._n_of_cows
        if options["type"] == "KVAR":
            max_cycles = options["values"]
        return max_cycles

    @property
    def _actual_cycle(self):
        options = self.jsonData["initial-conditions"]["cows"]["actual-cycle"]
        if options["type"] == "CONS":
            value = options["values"]
            actual_cycle = value*self._n_of_cows
        if options["type"] == "KVAR":
            actual_cycle = options["values"]
        return actual_cycle

    @property
    def _initial_time(self):
        options = self.jsonData["initial-conditions"]["cows"]["initial-time"]
        if options["type"] == "CONS":
            value = options["values"]
            initial_time = value*self._n_of_cows
        if options["type"] == "KVAR":
            initial_time = options["values"]
        return initial_time
    """
    END: Control Parameters.
    """
    @property
    def _lactant_model(self):
        return self.jsonData["initial-conditions"]["cows"]["lactant-model"]["values"]

    @property
    def _feeding_model(self):
        options = self.jsonData["initial-conditions"]["cows"]["feeding-model"]
        model = options["value"]
        parameters = []
        for param in self._FEEDING[model]:
            parameters.append(options["model"][param])
        parameters.append(model)

        return parameters



    @property
    def _concentrated_model(self):
        options = self.jsonData["initial-conditions"]["cows"]["concentrated-feeding"]["model"]
        parameters = [param for param in options["weights"]]
        return parameters



    @property
    def _rvs(self):
        # rvs: Random Variables
        rvs = self._RVS[self._lactant_model[0]]
        total_rvs = len(rvs)
        result = []
        distributions = []
        # result is a matrix that contain parameters of distribution and funtion
        # of ditribution, and that is related with a random variable
        for rv in rvs:
            options = self.jsonData["initial-conditions"]["cows"]["lactant-model"]["rvs"][rv]
            distribution = options["distribution"]
            distributions.append(self._distributions[distribution])

            parameters = options["parameters"]
            params = [0]*len(parameters)
            index = self._indexes[distribution]
            for key in options["parameters"]:
                params[index[key]] = parameters[key]
            params.append(distribution)
            result.append(params)

        return [result, distributions]

    def genCows(self):
        cows = []
        for n in range(self._n_of_cows):
            actual_cycle = self._actual_cycle[n]
            # It is not limited the simulation to max_num_cycles
            max_num_cycles = self._max_cycles[n]
            time_of_initial_cycle = self._initial_time[n]
            rvs_of_cow = [ np.abs( self._rvs[1][x](self._rvs[0][x]) ) for x in range( len(self._rvs[1]) ) ]
            # Assign attributes to each cow
            lactation_model = self._lactant_model[0]
            feeding_model = self._feeding_model

            concentrated_model = self._concentrated_model

            # It is time to consider input *args, or **kargs to include many models
            cows.append( Cow( time_of_initial_cycle, actual_cycle, max_num_cycles, rvs_of_cow , lactation_model, feeding_model, concentrated_model) )

        return cows
