import numpy as np
import pandas as pd
from scipy import stats

import argparse
import logging
logging.basicConfig(level = 'INFO')
logger = logging.getLogger(__name__)
# limpiar, histograma, y datos pendientes
from cow import Cow
from grid import SimulationGrid

from generator import Generator

# from test import student_ecuation


def main(JSONpath, result_path):
    #path = 'input/agro.json'
    """
    First part: Import data from agro.JSON and separate the data
    for cows and grid simulation
    """
    logger.info('Initializing individual simulation')
    # generator obtain data from JSON and determines the rules of game
    generator = Generator(JSONpath)
    # Prepare the environment of simulation
    cows = generator.genCows()
    grid = SimulationGrid(1, cows)

    grid.setProperties(generator)
    grid.setControlParameters(generator)

    """
    Simulation
    """
    simulation_times = generator._simul_times

    logger.info('Starting individual simulation')

    # (1, simulation_times.shape[0])
    vol_production = np.array([])
    active_cows = np.array([])
    concentrated_requirements = np.array([])
    grass_requirements = np.array([])
    # USAR EL FOR CON LAS INTERACIONES MONTECARLO INTERNAMENTE EN ESTE MODULO

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

        active = [cow.isCowActivated(time, grid.properties) for cow in grid.cows]
        vol = 0
        act = 0
        concentrated = 0
        grass = 0
        for i in range(generator._n_of_cows):
            if active[i]:
                act += 1
                vol += grid.cows[i].cowVolume(time)[0]
                concentrated += grid.cows[i].cowVolume(time)[1]
                grass += grid.cows[i].cowVolume(time)[2]
        vol_production = np.append(vol_production, vol)
        active_cows = np.append(active_cows, act)
        concentrated_requirements = np.append(concentrated_requirements, concentrated)
        grass_requirements = np.append(grass_requirements, grass)
    i=1
    for cow in grid.cows:
        print(i)
        print(cow._optimization_value)
        i += 1
    final_data = np.array([simulation_times, vol_production, active_cows, concentrated_requirements, grass_requirements])
    final_data = final_data.transpose()
    output_data = pd.DataFrame(final_data, columns=['Time (day)','Volume (Liters)', 'n active cows', 'concentrated_requirements', 'grass_requirements'], )

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
