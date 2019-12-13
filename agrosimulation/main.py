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


def main(JSONpath, optimization_path, output_path, iterations):
    #path = 'input/agro.json'
    """
    First part: Import data from agro.JSON and separate the data
    for cows and grid simulation
    """
    logger.info('Initializing individual simulation')
    # generator obtain data from JSON and determines the rules of game
    generator = Generator(JSONpath)
    # Prepare the environment of simulation

    initial_cows = generator.genCows()

    """
    MONTE CARLO Simulation
    """
    grid = SimulationGrid(1, initial_cows)

    grid.setProperties(generator)
    grid.setControlParameters(generator)


    simulation_times = generator._simul_times

    # Monte Carlo Simulation

    vol_production = np.array([])
    active_cows = np.array([])
    concentrated_requirements = np.array([])
    grass_requirements = np.array([])

    for time in simulation_times:

        active = [cow.isCowActivated(time, grid.properties) for cow in grid.cows]
        vol = 0
        act = 0
        concentrated = 0
        grass = 0
        for i in range(generator._n_of_cows):
            if active[i]:
                act += 1
                optim_params = grid.cows[i].cowVolume(time)
                vol += optim_params[0]
                concentrated += optim_params[1]
                grass += optim_params[2]
        vol_production = np.append(vol_production, vol)
        active_cows = np.append(active_cows, act)
        concentrated_requirements = np.append(concentrated_requirements, concentrated)
        grass_requirements = np.append(grass_requirements, grass)

    milk = 0
    c_milk = 0
    conc = 0
    c_conc = 0
    grass = 0
    c_grass = 0
    for cow in grid.cows:
        for array in cow._optimization_value:
            milk += array[0]
            conc += array[1]
            grass += array[2]
            c_milk += 1
            c_conc += 1
            c_grass += 1

    milk = milk / c_milk
    conc = conc / c_conc
    grass = grass / c_grass

    optimization = np.array([milk, conc, grass])
    final_data = np.array([simulation_times, vol_production, active_cows, concentrated_requirements, grass_requirements])
    final_data = final_data.transpose()
    output_data = pd.DataFrame(final_data, columns=['Time (day)','Volume (Liters)', 'n active cows', 'concentrated_requirements', 'grass_requirements'] )

    optimization_data = pd.DataFrame(optimization, index=['best milk', 'best concentrated', 'best grass'])
    output_data.to_csv(output_path, index=False)
    optimization_data.to_csv(optimization_path, index=False)
    logger.info('Individual results saved in {}'.format(output_path))
    logger.info('Optimization results saved in {}'.format(optimization_path))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('JSONpath',
                        help = 'Input JSON: agro.json',
                        type = str)
    parser.add_argument('optimization_path',
                        help = 'Number of iterations',
                        type = str)
    parser.add_argument('output_path',
                        help = 'Number of iterations',
                        type = str)
    parser.add_argument('iterations',
                        help = 'Number of iterations',
                        type = int)
    args = parser.parse_args()
    main(args.JSONpath, args.optimization_path, args.output_path, args.iterations)
