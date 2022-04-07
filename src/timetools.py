"""
All functions for reading time data
from input files
"""

import pandas as pd
import pytz
import datetime
import logging
import numpy as np

from config_parse import CONFIG, TIME_FORMATS

def convert(df, station):
    """
    Converts the groups of time columns
    into single datetime columns

    NOTE!!! Currently stamps all but UTC times to
    the given timezone
    """

    logging.debug('Converting time columns')

    # For each defined time format...
    for fmt in TIME_FORMATS:

        # Get the timezone of the time format
        timezone_string = CONFIG['time'][fmt]['timezone']
        fixed_offset = 0
        
        if timezone_string.lower()=='station':
            # The timezone for this time format has
            # been set to the timezone of the station
            fixed_offset = CONFIG['stations'][station]['offset']
            timezone_string = CONFIG['stations'][station]['timezone']

			
        try:
            # Copy time columns
            t = df[['year-'+fmt, 'month-'+fmt, 'day-'+fmt, 'hour-'+fmt, 'minute-'+fmt]]
            # Rename into generic titles
            t.columns = ['year', 'month', 'day', 'hour', 'minute']
            # Convert them to naive datetime objects
            df[fmt] = pd.to_datetime(t)

            if fmt == 'lst': # local standard time, no DST, use fixed offset
                timezone = pytz.FixedOffset(fixed_offset) # using fixed timezone offset, for dataset in local standard time (without daylight savings) http://www.bom.gov.au/climate/data-services/solar/content/data-time.html
            elif fmt == 'lt': # including DST, use timezone string
                timezone = pytz.timezone(timezone_string) # This function will also consider daylight savings. BOM data is in local standard time without daylight savings.
            elif fmt == 'utc':
                timezone = pytz.timezone('UTC')
            df[fmt] = df[fmt].dt.tz_localize(timezone, ambiguous='raise')

        except KeyError:
            logging.debug('Error with ' + fmt)
            pass

        # Delete the old time columns
        deleteGroup(df, fmt)

def deleteGroup(df, format):
    """
    Deletes a set of time columns
    Format decides on the suffix (utc, lst, lt)
    """
    cols = ['year-', 'month-', 'day-', 'hour-', 'minute-']
    for col in cols:
        try: del df[col+format]
        except KeyError: pass

def decideTimeColumn(df):
    """
    Decides which datetime column to use
    by checking how many null values each
    time column has
    Renames this column to 'datetime' and
    deletes all other time columns
    Returns True if it was successful
    """

    # Make a list of the number of null
    # values in each time column
    results = {}
    for fmt in TIME_FORMATS:
        if fmt in df:
            results[fmt] = df[fmt].isnull().sum()

    if not results:
        # No time columns were found. Quit
        logging.error('No time columns were found. Quitting this file')
        return False

    # Get the format with the smallest value
    keep = min(results, key=results.get)
    #keep = 'lst' # update -> always use LST as it is available in aw and sl - note the columns are without DST	
    logging.debug('Using time column "'+keep+'"')

    # Delete all but that column
    for fmt in results:
        if fmt!=keep: del df[fmt]

    # Rename the decided column
    df.rename(columns={keep:'datetime'}, inplace=True)

    return True

def generateTimeseries(year, month, timezone, df_type=True):
    """
    Generates minutely timeseries for one month
    Returns a DataFrame if df_type=True, a DateTimeIndex
    if df_type=False
    """

    logging.debug('Generating master timeseries')

    year = int(year)
    month = int(month)
    if month==12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    start = datetime.datetime(year, month, 1)
    end = datetime.datetime(next_year, next_month, 1)

    # freq=T means minutely
    # closed='left' means the right bracket is not
    # closed (end is inclusive)
    
    timeseries = pd.date_range(start, end, freq='T', inclusive='right', tz=timezone)
    if df_type:
        timeseries = pd.DataFrame(timeseries)
        timeseries.columns = ['datetime']
    return timeseries

def mergeAgainstMasterTimeseries(df, timeseries, right_on='datetime', left_on='datetime'):
    """
    Generates the master timeseries, then
    left joins a dataframe against a complete
    timeseries, ensuring each timestep is
    represented in the dataframe
    Returns a new dataframe
    """

    logging.debug('Merging against master timeseries')

    # Left-join the dataframe against the complete timeseries
    df = pd.merge(timeseries, df, how='left', right_on=right_on, left_on=left_on)

    # Make sure that the datetime column is datetime, not object
    df[left_on] = pd.to_datetime(df[left_on])

    return df
