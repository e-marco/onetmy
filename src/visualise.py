import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from math import ceil

import random

def missing_data(df, max_rows=50):
    """
    Plots NaN values in dataframe df as a heatmap

    If you want to simplify the graph by counting
    the number of NaN values for every n rows,
    set the maximum number of rows to plot using
    max_rows
    max_rows=0 is equivalent to max_rows=infinity
    """

    plt.rcParams.update({'font.size': 8})

    df = df.isnull()    # Find NaN values

    # If the number of rows is greater than
    # max_rows, 'collapse' the data, counting
    # the number of NaN values in each group.
    rows = df.shape[0]
    if rows>max_rows and max_rows!=0:
        # rows/i<max_rows, where i=int
        i = ceil(rows/max_rows)
        df = df.set_index(df.index // i).sum(level=0)
        sns.heatmap(df)
    else:
        sns.heatmap(df, cbar=False)

    plt.show()

if __name__=='__main__':

    # Open test dataset and randomly insert NaNs
    df = pd.read_csv('airline-safety.csv')
    rows, cols = df.shape
    for i in range(0, rows):
        for j in range(0, cols):
            if random.randint(0, 10)>8:
                df.iloc[i, j] = np.nan

    missing_data(df, 20)
