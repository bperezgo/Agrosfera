import argparse
import logging
logging.basicConfig(level = logging.INFO)

import pandas as pd
import numpy as np
from scipy.optimize import least_squares
import matplotlib.pyplot as plt


logger = logging.getLogger(__name__)

def main(filename):
    """
    This module takes the clean cow data and it will be transformed in frequencies
    to detect the distributions of all parameters. In this case it will be taken
    v_max, v_preg, t_max, lactant_time, dry_time*. These parameter it willbe adjusted
    to cuadratic function**.

    Notes:
        * v_max: max volume reached in the lactant curve
        * v_preg: Initial volume of the cow in the lactant curve
        * t_max: Time in which is reache v_max
        * lactant_time: Interval of time in which lactant curve is defined
        * dry_time: Interval of time in which the cow is not producing

        ** This argument must be generalized to several models
    """
    logger.info('Searching parameters of cows')
    clean_cow_data = pd.read_csv(filename)
    cows = clean_cow_data['COW'].unique()

    clean_cow_data['DAY'] = clean_cow_data['DATE'].apply(date_to_day)
    clean_cow_data = clean_cow_data.set_index(['COW', 'DAY'])

    lactant_curve = clean_cow_data['MILK']
    # cows = lactant_curve.index.levels[0]
    # days = lactant_curve.index.levels[1]

    lactant = np.array([])
    dry = np.array([])

    t_max = []
    V_max = []
    V_preg = []
    V_preg_cond_V_max = []
    # Extract parameters from the original data
    for cow in cows:

        lactant_curve_temp = lactant_curve.loc[cow]
        days, milks = getLactantCurve(lactant_curve_temp)
        lactant_time, dry_time = getGeneralParameters(days, milks)
        lactant = np.append(lactant, lactant_time)
        dry = np.append(dry, dry_time)
        model = 'cuadratic'
        for i in range(len(days)):
            t_train = np.array(days[i]) - days[i][0]
            y_train = np.array(milks[i])
            x0 = np.array([-1.0,1.0,1.0])
            # This values because "a" is negative generally and the others are positive
            params = getLactantParameters(model, x0 , t_train, y_train)
            # Eliminate values with a > 0
            t_max_fun = (- params[1] / (2*params[0]))
            V_max_fun = lambda t: params[0]*t*t + params[1]*t + params[2]
            V_max_temp = V_max_fun(t_max_fun)
            if params[0] > 0:
                continue
            if t_max_fun < 0:
                V_max.append(params[2])
                t_max.append(0.0)
                V_preg.append(params[2])
                V_preg_cond_V_max.append(0)
                continue
            V_preg_cond_V_max.append( (V_max_temp - params[2]) / V_max_temp )
            t_max.append(t_max_fun)
            V_max.append( V_max_temp )
            V_preg.append(params[2])

    print('--------')

    logger.info('The parameters were matching')
    # Extract the parameters of distributions of the 5 random variables
    elements = [t_max, V_preg, lactant, dry, V_preg_cond_V_max]
    result = pd.DataFrame(V_max)
    for element in elements:
        df = pd.DataFrame(element)
        result = result.join(df, lsuffix='_caller', rsuffix='_other')
    result.columns = ['V_max', 't_max', 'V_preg', 'lactant', 'dry', 'V_preg_cond_V_max']
    result.to_csv('results_clean_cow_data.csv', index = False)
    print(result)

def getGeneralParameters(days, milks):
    # function that returns time of the dry and lactant time
    n_curves = len(days)

    lactant_time = 0
    for n in range(n_curves):
        lactant_time = lactant_time + days[n][-1] - days[n][0]
    provisional_value = 365
    # It is supposed that lactant time plus dry time is equal to provisional_value
    dry_time = provisional_value - lactant_time
    return lactant_time, dry_time

def getLactantCurve(lactant_curve):
    # Obtain the curves with main information for a cow
    # Data must be descendent ordered with the time
    flag = True # It is True while is the data iterated
    flag2 = True # It is True while the value of the column is zero

    i = 0
    ind = lactant_curve.index[0]
    day = []
    days = []
    milk = []
    milks = []
    while flag:
        while flag2:
            # Only with .loc, DataFrame must have index name
            if lactant_curve.loc[ind] > 0:
                flag2 = False
            else:
                i += 1
                try:
                    ind = lactant_curve.index[i]
                except IndexError:
                    flag = False
                    flag2 = False

        while (not flag2) and flag:
            if lactant_curve.loc[ind] == 0:
                flag2 = True
                days.append(day)
                milks.append(milk)
                day = []
                milk = []
            else:
                day.append(ind)
                milk.append(lactant_curve.loc[ind])
                i += 1
                try:
                    ind = lactant_curve.index[i]
                except IndexError:
                    flag = False
                    flag2 = True
                    days.append(day)
                    milks.append(milk)
    return days, milks

def date_to_day(date):
    month = {'ene': 0, 'feb': 31, 'mar': 59, 'abr': 90, 'may': 120, 'jun': 151,
             'jul': 181, 'ago': 212, 'sep': 243, 'oct': 273, 'nov': 304, 'dic': 334, }
    date = date.split('-')
    day = int(date[0]) + month[date[1]]
    return day

def getLactantParameters(model, x0, *args):
    # it is necessary to have the lactant curve

    functions = {'cuadratic': lambda x, t, y: x[0]*t*t + x[1]*t +x[2] - y}

    fun = functions[model]
    result = least_squares( fun, x0, args= args).x
    return result

if __name__ == '__main__':
    print('inicio')
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help = 'file with the data of the cows',
                        type = str)
    args= parser.parse_args()
    main(args.filename)
