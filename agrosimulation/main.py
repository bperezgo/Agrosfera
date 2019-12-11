import numpy as np
import pandas as pd
from scipy import stats

import argparse
import logging
logging.basicConfig(level = 'INFO')
logger = logging.getLogger(__name__)
# Montecarlo, limpiar, histograma, y datos pendientes
from cow import Cow
from grid import SimulationGrid
"""
CRITERIO para definir la curva de lactancia con un modelo cuadrático

delta_V / Vpreg <= ( 2*(tL / t_max) + (tL / t_max)**2 )**(-1)

"""
# Extraigo Generator y JSONData
from JSON_data import *

# from test import student_ecuation


def main(JSONpath, result_path):
    #path = 'input/agro.json'
    """
    First part: Import data from agro.JSON and separate the data
    for cows and grid simulation
    """
    logger.info('Initializing individual simulation')
    data = JSONData(JSONpath)
    # Obtain data from JSON

    # Juez del juego
    generator = Generator(data)
    # Prepare the environment of simulation
    # The first value of grid doesn't import
    cows, dummy_data = generator.genCows()
    #print(dummy_data)
    grid = SimulationGrid(5634563, cows)

    grid.setProperties(generator)
    grid.setFunctions(generator)

    """
    Simulation
    """
    logger.info('Starting individual simulation')
    simulation_times = generator._simul_times
    # (1, simulation_times.shape[0])
    vol_production = np.array([])
    active_cows = np.array([])
    for time in simulation_times:

        """
        # This section is only to see how is behaving the simulator, for debugging
        if int(time) % 110 == 0:
            j = 0
            for cow in grid.cows:
                impresion = [cow._cuadratic_params,[cow.v_max, cow.v_preg, cow.t_max], cow.time_of_initial_cycle, cow.lactant_time, cow.dry_time, cow.final_time]
                print('---')
                print(student_ecuation(cow._cuadratic_params))
                print(j)
                print(impresion)
                print('---')
                j += 1
        """

        active = [cow.isCowActivated(time, grid.properties, grid.functions) for cow in grid.cows]
        vol = 0
        act = 0
        for i in range(generator._n_of_cows):
            if active[i]:
                act += 1
                vol += grid.cows[i].cowVolume(time)
        vol_production = np.append(vol_production, vol)
        active_cows = np.append(active_cows, act)


    final_data = np.array([simulation_times, vol_production, active_cows])
    final_data = final_data.transpose()
    output_data = pd.DataFrame(final_data, columns=['Time (day)','Volume (Liters)', 'n active cows'], )

    output_data.to_csv(result_path, index=False)
    logger.info('Individual results saved in {}'.format(result_path))
    return output_data

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('JSONpath',
                        help = 'Input JSON: agro.json',
                        type = str)
    parser.add_argument('resultpath',
                        help = 'Name of the file to output',
                        type = str)
    args = parser.parse_args()
    main(args.JSONpath, args.resultpath)
