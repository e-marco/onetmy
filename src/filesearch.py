"""
This file contains one function that is used to search
for data files. Edit it to make it work for you
"""

import os
import re
import datetime
import logging

def run(dir, pattern):
    """
    Searches for files in a directory that match a
    given regex pattern. This pattern must include
    at least two groups that match integers:

    - The first one that is <=12 is considered the
    month
    - The first one that is >12 is considered the
    year

    Returns the matches as a dictionary with
    datetimes as the key (accurate to the month) and
    file paths as the value
    """

    logging.info('Searching for data files')

    if not os.path.isdir(dir):
        raise FileNotFoundError(dir)

    pattern = re.compile(pattern)

    matches = {}

    for r, d, f in os.walk(dir):
        for file in f:
            path = os.path.normpath(os.path.join(r, file))
            match = pattern.match(path)
            if match!=None:

                # We have a match
                # The first group with an integer <=12 is
                # considered the month, the first with an
                # integer >12 is considered the year
                year = None
                month = None
                for group in match.groups():
                    try:
                        tmp = int(group)
                        if tmp>12:
                            year = tmp
                        else:
                            month = tmp
                    except ValueError:
                        # Couldn't be turned into an integer
                        pass

                # Now hopefully both year an month have been
                # set. Otherwise, don't add this file
                if year!=None and month!=None:
                    logging.debug('File match: '+str(path))
                    key = datetime.datetime(year, month, 1)
                    # If there's already a file for this month,
                    # don't overwrite its value!
                    if key in matches:
                        matches[key].append(path)
                    else:
                        matches[key] = [path]
                else:
                    logging.warning('Year and month not found in match: '+path)

    return matches

if __name__=='__main__':
    dir = 'C:/Users/Jack/Music/003003'
    pattern = '.*(sl|aw)_003003_(\d{4})_(\d{2}).csv'
    run(dir, pattern)
