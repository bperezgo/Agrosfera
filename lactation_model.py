import RVS

class LactationModel():

    def __init__(self, model):
        """
        _rvs: private attributes that have necessary variables for the model
        """
        self._model =  model
        self._rvs = {
                        "CUADRATIC": self._cuadraticRVS
        }
        self._conditions = {
                        "CUADRATIC": self._cuadraticConditions
        }
        self._models = {
                        "CUADRATIC": self._cuadraticModel
        }

    @property
    def model(self):
        return self._models[self._model]

    @property
    def RVS(self):
        V0_Vd
        delta_V
        tL_tmax


    @property
    def _cuadratic_params(self):
        a = (self.v_preg - self.v_max) / (self.t_max * self.t_max)
        b = - 2 * a * self.t_max
        return [a , b, self.v_preg]

    def _cuadraticModel(self):
        """
        Requirement in the cuadratic model

        delta_V / Vpreg <= ( 2*(tL / t_max) + (tL / t_max)**2 )**(-1)
        delta_V : V_max - (V0 - VD)
        """


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

    def _cuadraticConditions(self):
        """

        """
