import json

import numpy as np

from cow import Cow

class JSONData():
    # This module can be transport to simulation.py to optimize this code
    # and use this object like enter parameter of the function main.py in agrosimulation
    def __init__(self,path):
        self.path = path

    @property
    def dict_obj(self):
        with open(self.path, 'r') as f:
            data=f.read()
        return json.loads(data)

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


class Generator():

    def __init__(self, jsonData):
        self.jsonData = jsonData

        self._distributions = { "EXPONENTIAL": _expAtributes,
                                "NORMAL": _normalAtributes,
                                "LOGISTIC": _logisticAtributes,
                                "POISSON": _poissonAtributes,
                                "GAMMA": _gamAtributes
                      }
        self._indexes = {
                            "EXPONENTIAL": {"lambda": 0},
                            "NORMAL": {"mean": 0, "std": 1},
                            "LOGISTIC": {"mean": 0, "scale": 1},
                            "POISSON": {"lambda": 0},
                            "GAMMA": {"shape": 0, "scale": 1}
        }

    @property
    def ID(self):
        return self.jsonData.dict_obj["grid-simulation"]["timeimp"]["ID"]

    @property
    def _simul_times(self):
        return np.array(self.jsonData.dict_obj["grid-simulation"]["timeimp"])

    @property
    def _lactant_model(self):
        return self.jsonData.dict_obj["initial-conditions"]["cows"]["lactant-model"]["values"]

    """
    _max_cycles, _actual_cycle, _initial_time_cow needs new modifications because
    are control parameters
    """
    @property
    def _max_cycles(self):
        return self.jsonData.dict_obj["initial-conditions"]["cows"]["max-cycles"]["values"]

    @property
    def _actual_cycle(self):
        return self.jsonData.dict_obj["initial-conditions"]["cows"]["actual-cycle"]["values"]

    @property
    def _intial_time_params(self):
        # This seems that is not used
        options = self.jsonData.dict_obj["initial-conditions"]["cows"]["initial-time"]
        params = []
        if options["model"] == "UNIFORM":
            params.append(options["parameters"]["t-max"])
            params.append(options["parameters"]["t-initial"])

        return params

    @property
    def _max_volume(self):
        options = self.jsonData.dict_obj["initial-conditions"]["cows"]["v_max"]
        distribution = options["distribution"]
        parameters = options["parameters"]
        params = [0]*len(parameters)
        index = self._indexes[distribution]
        """
        En el JSON debe conservarse el orden de los parámetros, eso no lo
        hace escalable
        """
        for key in options["parameters"]:
            params[index[key]] = parameters[key]
        params.append(distribution)
        return params

    @property
    def _max_time(self):
        options = self.jsonData.dict_obj["initial-conditions"]["cows"]["t_max"]
        distribution = options["distribution"]
        parameters = options["parameters"]
        params = [0]*len(parameters)
        index = self._indexes[distribution]
        """
        En el JSON debe conservarse el orden de los parámetros, eso no lo
        hace escalable
        """
        for key in options["parameters"]:
            params[index[key]] = parameters[key]
        params.append(distribution)
        return params

    @property
    def _pregnant_volume(self):
        options = self.jsonData.dict_obj["initial-conditions"]["cows"]["v_preg"]
        distribution = options["distribution"]
        parameters = options["parameters"]
        params = [0]*len(parameters)
        index = self._indexes[distribution]
        """
        En el JSON debe conservarse el orden de los parámetros, eso no lo
        hace escalable
        """
        for key in options["parameters"]:
            params[index[key]] = parameters[key]
        params.append(distribution)
        return params


    @property
    def _lactant_time(self):
        options = self.jsonData.dict_obj["initial-conditions"]["cows"]["lactant-time"]
        distribution = options["distribution"]
        parameters = options["parameters"]
        params = [0]*len(parameters)
        index = self._indexes[distribution]
        """
        En el JSON debe conservarse el orden de los parámetros, eso no lo
        hace escalable
        """
        for key in options["parameters"]:
            params[index[key]] = parameters[key]
        params.append(distribution)
        return params

    @property
    def _dry_time(self):
        options = self.jsonData.dict_obj["initial-conditions"]["cows"]["dry-time"]
        distribution = options["distribution"]
        parameters = options["parameters"]
        params = [0]*len(parameters)
        index = self._indexes[distribution]
        """
        En el JSON debe conservarse el orden de los parámetros, eso no lo
        hace escalable
        """
        for key in options["parameters"]:
            params[index[key]] = parameters[key]
        params.append(distribution)
        return params

    @property
    def _pregnant_time(self):
        options = self.jsonData.dict_obj["initial-conditions"]["cows"]["pregnant-time"]
        distribution = options["distribution"]
        parameters = options["parameters"]
        params = [0]*len(parameters)
        index = self._indexes[distribution]
        """
        En el JSON debe conservarse el orden de los parámetros, eso no lo
        hace escalable
        """
        for key in options["parameters"]:
            params[index[key]] = parameters[key]
        params.append(distribution)
        return params

    @property
    def _pregnant_duration(self):
        options = self.jsonData.dict_obj["initial-conditions"]["cows"]["pregnant-duration"]
        return options["value"]

    @property
    def _n_of_cows(self):
        return self.jsonData.dict_obj["initial-conditions"]["cows"]["number"]

    def _initial_time_cow(self, interval_len):
        value = np.random.random(1)[0]
        return (value*2 - 1)*interval_len
    """
    calculation are not generalized in genCows
    """
    def genCows(self):
        cows = []
        """data_dummy is only for testing"""
        data_dummy = []
        for n in range(self._n_of_cows):
            # The last term in the list is the distribution for the variable

            v_max = np.abs(self._distributions[self._max_volume[-1]](self._max_volume[0:-1]))
            t_max = np.abs(self._distributions[self._max_time[-1]](self._max_time[0:-1]))
            v_preg = np.abs(self._distributions[self._pregnant_volume[-1]](self._pregnant_volume[0:-1]))
            if v_preg > v_max:
                # In this part v_max has the minimum value
                temp = v_max
                v_max = v_preg
                v_preg = temp

            lactation_model = self._lactant_model[0]
            actual_cycle = self._actual_cycle[0]
            # It is not limited the simulation to max_num_cycles
            max_num_cycles = self._max_cycles[0]
            lactant_time = np.abs(self._distributions[self._lactant_time[-1]](self._lactant_time[0:-1]))
            dry_time = np.abs(self._distributions[self._dry_time[-1]](self._dry_time[0:-1]))
            # hope to find another form to stimate initial time of the cycle
            time_of_initial_cycle = self._initial_time_cow(lactant_time + dry_time)
            initial_time_in_preg = np.abs(self._distributions[self._pregnant_time[-1]](self._pregnant_time[0:-1]))
            preg_duration = self._pregnant_duration

            cows.append( Cow(v_max, t_max, v_preg, lactation_model, time_of_initial_cycle, actual_cycle, max_num_cycles, lactant_time, dry_time, initial_time_in_preg, preg_duration) )

            data_dummy.append([v_max, t_max, v_preg, time_of_initial_cycle, lactant_time, dry_time])
        return cows, data_dummy;
