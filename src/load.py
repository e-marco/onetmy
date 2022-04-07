import os
import re
import pandas as pd
import logging
import pytz

from config_parse import CONFIG, HEADER_MAP
import timetools, flagtools

def stripRenameColumns(df):
    """
    Renames all of the columns in a data file, and
    removes any that aren't needed
    Applys these changes in-place
    CONFIG is the configuration file
    """

    logging.debug('Stripping and renaming columns')

    # The mapping of the old headers
    # to the new ones has been imported
    # from config_parse.py - HEADER_MAP

    # Rename columns
    for new_header in HEADER_MAP:
        old_header = HEADER_MAP[new_header]
        if old_header in df:
            df.rename(columns={old_header:new_header}, inplace=True)

    # Delete columns that aren't needed
    current_headers = list(df)
    allowed_headers = list(HEADER_MAP.keys())
    for current_header in current_headers:
        if current_header not in allowed_headers:
            #logging.info('Deleting '+ current_header)
            del df[current_header]



def load(paths, station, year, month):
    """
    Loads any data it finds for a specific month
    and location. Returns one dataframe

    paths - list of file paths that contain data for
        this month
    station - name of the station. used to reference
        the config.yml file
    year and month - year and month we are loading
        data for
    """

    logging.info('Loading %s %s/%s', str(station), str(year), str(month))

    # Make the timeseries for this month
    offset = CONFIG['stations'][station]['offset']
    timezone = pytz.FixedOffset(offset)
    timeseries = timetools.generateTimeseries(year, month, timezone)

    # Clean each file
    dataFiles = []
    logging.debug(paths)
	
    for path in paths:

        logging.debug('Loading %s', path)

        df = pd.read_csv(path, low_memory=False)

        # Rename and delete useless columns
        stripRenameColumns(df)

        # If the dataframe is now empty, stop
        if df.empty:
            logging.debug('Loading file "'+path+'" has resulted in an empty dataframe. Ignoring this file')
            continue

        # Convert time columns into datetimes
        timetools.convert(df, station)

        # Decide on which time column to use
        q = timetools.decideTimeColumn(df)
        if not q:
            # Couldn't decide time column
            # Quit this file
            continue

        # Convert the flags columns
        flagtools.convert(df)

        # Mask data against flags
        flagtools.maskData(df)

        # Delete the flag columns
        flagtools.deleteFlagColumns(df)
        # Convert all columns to numeric
        # APART FROM the datetime column
        cols = [x for x in list(df) if x!='datetime']
        df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

        # Merge against master timeseries
        df = timetools.mergeAgainstMasterTimeseries(df, timeseries)
        dataFiles.append(df)

    if not dataFiles:
        logging.warning('No files successfully loaded for %d/%d', year, month)
        return

    # Merge all of the found datafiles
    df = dataFiles[0]
    del dataFiles[0]
    for df2 in dataFiles:
        df = pd.merge(df, df2, right_on='datetime', left_on='datetime')

    # Set index to the datetime. This now means all
    # columns are numerical dtypes, therefore you can
    # interpolate without errors
    df.set_index('datetime', inplace=True)

    return df
