"""
Reads the configuration file config.yml
so that other modules can access the
configuration quickly
"""

import yaml

def timeHeaderMap():
    """
    Makes new time headers (used when
    renaming columns)
    Returns a dictionary mapping the
    old headers to the new ones
    """
    tmp = CONFIG['time']
    time_headers = {}
    for time_format in tmp:
        components = tmp[time_format]['file_format']
        for new_header in components:
            old_header = components[new_header]
            time_headers[new_header+'-'+time_format] = old_header
    return time_headers

def weatherHeaderMap():
    return CONFIG['weather']

def solarHeaderMap():
    return CONFIG['solar']

def makeHeaderMap():
    """
    Creates a complete header mapping
    old header -> new header
    """
    return {**timeHeaderMap(), **weatherHeaderMap(), **solarHeaderMap()}


# Load the configuration file
path = 'config.yml'
with open(path, 'r') as ymlfile:
    CONFIG = yaml.load(ymlfile, Loader=yaml.Loader)

# Dictionary of old headers -> new headers
HEADER_MAP = makeHeaderMap()

# List of time formats (utc, lst, lt etc.)
TIME_FORMATS = list(CONFIG['time'].keys())
