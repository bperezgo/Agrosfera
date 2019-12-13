import argparse
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from fitter import Fitter


def main():
    # NO agrega el último valor
    # Intervalos de confianza
    # distribucion de los datos de salida, cuáles distribuciones se ajustan

    test_distributions = ['gamma', 'rayleigh', 'uniform', 'normal']
    files = []
    summary = []
    for file in os.listdir("temp"):
        if file.endswith(".csv"):
            path = 'temp/' + file
            files.append(path)

    total_files = len(files)
    results = pd.read_csv(files[0], index_col = False).set_index('Time (day)')
    summary.append(results.apply(np.sum))
    for i in range(1,total_files):
        results_temp = pd.read_csv(files[i], index_col = False).set_index('Time (day)')
        summary.append(results_temp.apply(np.sum))
        results = results + results_temp
    print(summary)
    summary_df = pd.DataFrame(summary)
    results = results / total_files

    final_year = results.index[-1] - 365
    final_year_df = results.loc[final_year:]
    summary = final_year_df['Volume (Liters)'].apply(np.sum)
    final_year_df.to_csv('final_year_df.csv')
    results.to_csv('results.csv')
    summary_df.to_csv('summary.csv')

    summary_df = summary_df / 3

    f = Fitter(summary_df['Volume (Liters)'].values, distributions=test_distributions)
    f.fit()


    plt.figure(figsize = [8, 6])
    plt.plot(results)
    plt.xlabel('Time (day)')
    plt.ylabel('Total volume (liters)')
    plt.legend(results.columns)
    plt.figure(figsize = [8, 6])
    plt.plot(final_year_df)
    plt.xlabel('Time (day)')
    plt.ylabel('Total volume last year (liters)')
    plt.legend(final_year_df.columns)
    plt.figure(figsize = [8, 6])
    sns.distplot(summary, bins = total_files)
    print(f.summary())
    print(f.get_best())
    plt.show()
    plt.figure(figsize = [8, 6])
    f.hist()
    plt.show()

if __name__ == '__main__':
    main()
