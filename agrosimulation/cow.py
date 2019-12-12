import numpy as np
from scipy.interpolate import interp1d

def _simpsonsMethod(function, interval):
    # Rule of Simpson to calculate area down the curve
    n = int( ( interval[1] - interval[0] ) / 2 )
    h = 2.0 # days
    sum1 = 0
    sum2 = 0
    for i in range(1, int(n/2) + 1):
        evaluate = h/2*(2*i - 1)
        sum1 += function(evaluate)
    for i in range(1,int(n/2)):
        evaluate = h*2*i
        sum2 += function(evaluate)

    integral = function(0) + function(h*n) + 2 * sum2 + 4 * sum1
    integral = integral * h / 6
    return integral

def _cuadraticLactationModel(params):
    """
    params: Is the same of self.rvs_of_cow

    CRITERION: definition of restrictions of cuadratic model in Lactant model

    delta_V / (Vinitial - Vdry) <= ( 2*(tL / t_max) + (tL / t_max)**2 )**(-1)
    delta_V = Vmax - (Vinitial - Vdry)
    """
    t_max = params[3] / params[2]
    v_initial = params[1] + params[0]
    v_max = params[1] + params[1] * ( 1 / (2*params[2] + params[2]*params[2] ) )
    a = (v_initial - v_max) / (t_max * t_max)
    b = - 2 * a * t_max
    fun = lambda time: a * time * time + b * time + v_initial
    return fun

def _concentratedModel(params, volume_fun):
    concentrated_fun = lambda time: params[1]*volume_fun(time) + params[2]
    return concentrated_fun

def _simplifiedCornellModel(params, final_time):
    """
    Order of parameters in this model
    ["weight-of-cow", "reference-weight", "fat-percentage", "milk-density"]
    """
    weight_cow_curve = interp1d(params[0][0], params[0][1])
    FCM = lambda Volume: 0.4*Volume*params[3] + (15*Volume*params[2])/100
    #fun  = lambda time, Volume: 0.0185*weight_cow_curve(time / final_time) + 0.305*FCM(Volume)
    fun  = lambda time, Volume: 0.0185*600 + 0.305*FCM(Volume)
    return fun

class Cow(object):

    def __init__(self, time_of_initial_cycle, actual_cycle, max_num_cycles,
                       rvs_of_cow, lactant_model, feeding_model, concentrated_model):
        """
        rvs_of_cow: estimate of each of one parameter in the lactant model choosen,
                is a array, these componentes are:
                ["dry-volume", "delta-Vo-Vd", "tL-tmax-ratio", "lactant-time", "dry-time"]
        """
        self.rvs_of_cow             = rvs_of_cow

        self.lactant_model          = lactant_model
        self.feeding_model          = feeding_model
        self.concentrated_model     = concentrated_model

        self.time_of_initial_cycle  = time_of_initial_cycle
        self.actual_cycle           = actual_cycle
        self.max_num_cycles         = max_num_cycles

        self._optimization_value    = []

        self._lactant_models = {
            "CUADRATIC": _cuadraticLactationModel
        }
        self._feeding_models = {
            "CORNELL-SIMPLIFIED": _simplifiedCornellModel
        }

    @property
    def final_time(self):
        t0 = self.time_of_initial_cycle
        tL = self.rvs_of_cow[-2]
        tD = self.rvs_of_cow[-1]
        tf = t0 + tL + tD
        return tf

    @property
    def _lactant_function(self):

        def internal_function(time):
            fun = self._lactant_models[self.lactant_model](self.rvs_of_cow)
            if fun(time) < 0:
                return 0
            return fun(time)
        return internal_function

    @property
    def _concentrated_function(self):
        fun = _concentratedModel(self.concentrated_model, self._lactant_function)
        return fun

    @property
    def _feeding_function(self):
        return self._feeding_models[self.feeding_model[-1]](self.feeding_model[0:-1], self.final_time - self.time_of_initial_cycle)

    def cowVolume(self, actual_time):
        time = actual_time - self.time_of_initial_cycle
        if actual_time < (self.time_of_initial_cycle + self.rvs_of_cow[-2]):
            volume = self._lactant_function(time)
            # if volume < 0:
            #     volume = 0
            if time - 1 < 0:
                time = 1.01
            feeding = self._feeding_function(time - 1, volume)
            concentrated = self._concentrated_function(time - 1)
            grass = feeding - concentrated
        else:
            volume = 0
            feeding = self._feeding_function(time - 1, volume)
            concentrated = self._concentrated_function(time - 1)
            return [0, feeding, concentrated]
        return [volume, concentrated, grass]

    def isCowActivated(self, actual_time, properties):
        if self.time_of_initial_cycle > actual_time:
            return False
        else:
            if actual_time < self.final_time:
                pass
            else:
                self.time_of_initial_cycle = self.final_time
                self.genNewCow_(properties)
                self._optimization_value.append(self._optimizationFunction())
            return True

    def _optimizationFunction(self):

        interval = (self.time_of_initial_cycle, self.final_time)
        volume = (_simpsonsMethod(self._lactant_function, interval))
        def feeding(time):
            volume_function = self._lactant_function(time)
            return self._feeding_function(time, volume_function)
        def concentrated_fun(time):
            volume_function = self._lactant_function(time)
            return self._feeding_function(time, volume_function) - self._concentrated_function(time)
        grass_fun = lambda time: feeding(time) - concentrated_fun(time)
        conc_matter = _simpsonsMethod(concentrated_fun, interval)
        grass_matter = _simpsonsMethod(grass_fun, interval)
        cycle_time = interval[1] - interval[0]
        result = [volume / cycle_time, conc_matter / cycle_time, grass_matter / cycle_time]
        return result

    def genNewCow_(self, properties):
        self.rvs_of_cow = [ np.abs( properties[1][x](properties[0][x]) ) for x in range( len(properties[1]) ) ]
        self.actual_cycle = self.actual_cycle + 1
        if self.actual_cycle > self.max_num_cycles:
            _disease_function()
        self.lactant_time = self.rvs_of_cow[-2]
        self.dry_time = self.rvs_of_cow[-1]

    def _disease_function(self):
        # AUN NO SE COMO PROGRAMARLA, NECESARIO PARA SACAR VACAS DE PRODUCCION
        return False

    def _arrive_function(self):
        # AUN NO SE COMO PROGRAMARLA, NECESARIO PARA SACAR VACAS DE PRODUCCION
        return False
