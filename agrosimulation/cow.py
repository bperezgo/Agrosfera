import numpy as np

class Cow(object):

    def __init__(self, v_max, t_max, v_preg, lactation_model, time_of_initial_cycle,
                       actual_cycle, max_num_cycles, lactant_time, dry_time, initial_time_in_preg, preg_duration):

        self.v_max                  = v_max
        self.t_max                  = t_max
        self.v_preg                 = v_preg
        self.lactation_model        = lactation_model
        self.time_of_initial_cycle  = time_of_initial_cycle
        self.actual_cycle           = actual_cycle
        self.max_num_cycles         = max_num_cycles
        self.lactant_time           = lactant_time
        self.dry_time               = dry_time
        self.initial_time_in_preg   = initial_time_in_preg
        self.preg_duration          = preg_duration

    @property
    def _cuadratic_params(self):
        a = (self.v_preg - self.v_max) / (self.t_max * self.t_max)
        b = - 2 * a * self.t_max
        return [a , b, self.v_preg]

    @property
    def final_time(self):
        t0 = self.time_of_initial_cycle
        tL = self.lactant_time
        tD = self.dry_time
        tf = t0 + tL + tD
        return tf

    def cowVolume(self, actual_time):
        # Revisar _final_time, debe tomarse el valor donde termina la lactancia
        if actual_time < (self.time_of_initial_cycle + self.lactant_time):
            fun = lambda params, t: params[0]*t*t + params[1]*t + params[2]
            time = actual_time - self.time_of_initial_cycle
            volume = fun(self._cuadratic_params, time)
            if volume < 0:
                return 0
            return volume
        else:
            return 0

    def isCowActivated(self, actual_time, properties, funs):
        if self.time_of_initial_cycle > actual_time:
            return False
        else:
            if actual_time < self.final_time:
                return True
            else:
                self.time_of_initial_cycle = self.final_time
                self.genNewCow_(properties,funs)
                return True

    def genNewCow_(self, properties, funs):
        # funs = [Generator._normalAtributes, Generator._expAtributes]
        v_max = np.abs(funs[0](properties[0]))
        self.t_max = np.abs(funs[1](properties[1]))
        v_preg = np.abs(funs[2](properties[2]))
        if v_preg > v_max:
            self.v_max = v_preg
            self.v_preg = v_max
        else:
            self.v_max = v_max
            self.v_preg = v_preg
        self.actual_cycle = self.actual_cycle + 1
        self.lactant_time = np.abs(funs[3](properties[3]))
        self.dry_time = np.abs(funs[4](properties[4]))
        self.initial_time_in_preg = np.abs(funs[5](properties[5]))
