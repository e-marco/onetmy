import pandas as pd
import numpy as np

def createCDF(df):
    """
    Returns a new dataframe with the same columns,
    and the CDF as the index.
    This is achieved by sorting all of the columns,
    then making a new index
    """
    # We can ignore the date for all of this
    #del df['datetime']

    # Sort all columns
    df = pd.DataFrame(np.sort(df.values, axis=0), columns=df.columns)

    # Turn the index into the CDF
    df.index = df.index/df.shape[0]

    return df

def calculateFS(lt_CDF, candidate_CDF):
    """
    Calculates the FS statistic for a candidate CDF
    against the long term CDF
    """

    # Move the index of each (the CDF percentages)
    # into their own columns
    lt_CDF = lt_CDF.reset_index()
    lt_CDF.columns = ['lt_CDF', 'measurement']
    candidate_CDF = candidate_CDF.reset_index()
    candidate_CDF.columns = ['candidate_CDF', 'measurement']

    # Drop any duplicates. The first entry is kept
    # I would just jump to the next step, but generally
    # the datasets are too large to join
    candidate_CDF.drop_duplicates(subset='measurement', inplace=True)
    lt_CDF.drop_duplicates(subset='measurement', inplace=True)

    # Left join candidate_CDF < lt_CDF on the
    # measured values (e.g. GHI). This should
    # result in three columns: lt_CDF,
    # candidate_CDF and the corresponding
    # measured values
    X = pd.merge(candidate_CDF, lt_CDF, how='left', on='measurement')

    difference_vector = X['lt_CDF']-X['candidate_CDF']
    sum_difference = difference_vector.sum()
    return abs(sum_difference)
