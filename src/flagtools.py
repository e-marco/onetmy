"""
Holds all functions for reading flags in
data files
"""

import logging

def convert(df):
    """
    Converts all columns with '-flag' in
    their header into boolean flags (often
    they're strings like 'Y', 'N', 'X')
    See flagMap if you want to modify this to
    convert different types of flags
    """

    logging.debug('Converting to binary flags')

    flagColumns = [x for x in list(df) if '-flag' in x]
    for flagColumn in flagColumns:
        df[flagColumn] = df[flagColumn].apply(map)

def map(x):
    """
    Converts a column of flags (possibly a set of
    charcaters) into boolean values
    flagColumn is the name of the column you want to convert
    """
    if x=='Y': return True
    else: return False

def maskData(df):
    """
    Goes through data-flag column pairs and
    deletes data values with unacceptable flag
    values
    """

    logging.debug('Masking against flags')

    flagColumns = [x for x in list(df) if '-flag' in x]
    dataColumns = [x[:-5] for x in flagColumns]
    for i in range(0, len(flagColumns)):
        dataColumn = dataColumns[i]
        flagColumn = flagColumns[i]
        # .mask replaces each index with flag TRUE with
        # NaN by default. Hence we negate the flag column
        if not df[flagColumn].empty:
            df[dataColumn] = df[dataColumn].mask(~df[flagColumn])
        else:
            # Flag column corrupt, assume all correct
            logging.warning('Flag column empty. Assuming all flags positive')

def deleteFlagColumns(df):
    """
    Deletes all of the flag columns in a
    dataframe
    """

    logging.debug('Deleting flag data')

    flagColumns = [x for x in list(df) if '-flag' in x]
    for x in flagColumns:
        del df[x]
