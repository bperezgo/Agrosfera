# https://docs.scipy.org/doc/numpy-1.15.0/reference/routines.random.html

import argparse
import subprocess
import logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)
from datetime import datetime

def main(JSON, output, iterations):
    initial_time_exe = datetime.now()
    """
    Entries that is possible to have in a interface
    """
    try:
        subprocess.run(['del', '/f', '*.csv'], cwd = './agrosimulation/temp', shell = True)
    except FileNotFoundError:
        logger.info('temp in agrosimulation is empty')
    try:
        subprocess.run(['del', '/f', '*.csv'], cwd = './analyze/temp', shell = True)
    except FileNotFoundError:
        logger.info('temp in analyze is empty')

    logger.info('Inizializing MONTE CARLO Simulation')
    i = 1
    while i < iterations + 1:
        temp_path = output + str(i) + '.csv'
        logger.info('Inizializing simulation number {}'.format(i))
        _executeSimulation(JSON, temp_path)
        i += 1

    _last_records(initial_time_exe)
    _moveFiles()
    _analyzeSimulations()
    #_moveGeneralResults(initial_time_exe)
    logger.info('MONTE CARLO Simulation FINISHED')

    final_time_exe = datetime.now()
    total_time = final_time_exe - initial_time_exe
    logger.info('{} was the time of Simulation'.format(total_time))

def _moveGeneralResults(time):
    logger.info('Moving general data')
    subprocess.run()
    path_file = ('results' + time.strftime("%m") + '-' + time.strftime("%d") + '-' +
        time.strftime("%y") + '_' + time.strftime("%H") + 'h-' + time.strftime("%M") + 'm')
    subprocess.run(['mkdir', path_file], cwd = './last-records', shell = True)
    subprocess.run(['xcopy', r'analyze\*.csv', r'.\last-records\{}\data'
    .format(path_file)], cwd = '.', shell = True)

def _executeSimulation(JSON, temp_path):
    subprocess.run(['python', 'main.py',JSON, temp_path], cwd = './agrosimulation')

def _last_records(time):
    logger.info('Creating temporal data for the results')
    path_file = ('results' + time.strftime("%m") + '-' + time.strftime("%d") + '-' +
        time.strftime("%y") + '_' + time.strftime("%H") + 'h-' + time.strftime("%M") + 'm')
    subprocess.run(['mkdir', path_file], cwd = './last-records', shell = True)
    subprocess.run(['mkdir', 'data'], cwd = './last-records/{}'
    .format(path_file), shell = True)
    subprocess.run(['mkdir', 'figures'], cwd = './last-records/{}'
    .format(path_file), shell = True)
    subprocess.run(['xcopy', r'agrosimulation\temp', r'.\last-records\{}\data'
    .format(path_file)], cwd = '.', shell = True)

def _moveFiles():
    logger.info('Moving files to analyze')
    subprocess.run(['xcopy', r'agrosimulation\temp', r'analyze\temp'], cwd = '.', shell = True)

    subprocess.run(['del', '/f', '*.csv'], cwd = './agrosimulation/temp', shell = True)

def _analyzeSimulations():
    logger.info('Analyzing MONTE CARLO Simulation')
    subprocess.run(['python', 'main.py'], cwd = './analyze')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('iterations',
                        help = 'Introduce JSON',
                        type = int)
    args = parser.parse_args()
    main('input/agro.json', 'temp/result', args.iterations)
