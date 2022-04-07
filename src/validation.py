import logging
import datetime

def month(dates, required_n):
    """
    Checks to see if we have enough years for this
    specific calendar month
    """

    logging.info('Validating calendar month has enough years')

    # If there's nothing in the list, fail immediately
    if not dates:
        logging.info('Validation failed (dates list empty)')
        return False

    month = dates[0].month    # Used to check all dates are the same month
    sum = 0

    for x in dates:
        if x.month == month:
            sum += 1
        else:
            logging.error('"dates" has datetime objects with different calendar months')
            raise ValueError('"dates" has datetime objects with different calendar months')

    result = sum>=required_n
    logging.debug('Validation result: '+str(result))
    return result


def months(dates, required_n):
    """
    Checks to see if we have enough years for each
    calendar month
    Returns True or False
    Logs number for each month
    'dates' is a list of datetime.datetime objects
    """

    logging.info('Validating enough months are available')

    dates = sorted(dates)
    enough = True
    output = ''
    for month in range(1, 13):
        n = len([x for x in dates if x.month==month])
        enough = n>=required_n
        month_name = datetime.datetime(2000, month, 1).strftime('%B')

        output += '\n\t'+month_name.ljust(9)+'\t'+str(n)+'\t'+str(enough)

    logging.debug(output)
    logging.info('Validation result = '+str(enough))

    return enough

def dataAvailable(df, required_percentage):
    """
    Determines if the columns of a dataframe have
    the required percentage of data (i.e. isn't full
    of heaps of NaNs)
    required_percentage is the percentage of data
    you require, not the percentage of missing data
    """
    percentage_available = 1-(df.isnull().sum()/df.shape[0])
    logging.debug('Data available:\n'+str(percentage_available))
    return percentage_available>=required_percentage

def removePatchyColumns(df, required_percentage):
    """
    Removes any columns from a dataframe that
    don't have the required percentage of data
    """

    logging.debug('Checking completeness of columns')

    # Run the test
    test = dataAvailable(df, required_percentage)
    # Delete any column that didn't pass
    for column, result in test.items():
        if not result:
            logging.debug("Removing column '"+str(column)+"' as it doesn't have enough data")
            del df[column]

def requiredColumns(df):
    """
    Checks that a dataframe has all of
    the columns listed in list_of_cols
    Returns a bool
    Required you to initialise the global
    list of required columns
    """
    global required_cols
    return set(required_cols).issubset(df.columns)

"""required_cols = ['mean-ghi', 'mean-dni', 'mean-dhi',
    'air-temp', 'relative-humidity', 'wind-speed']
"""
required_cols = ['mean-ghi', 'mean-dni', 'mean-dhi',
    'air-temp', 'relative-humidity']
