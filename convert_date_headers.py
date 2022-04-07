"""
Converts the dumb time column names in BoM data file
to ones that make sense

In BoM files you have five sequential time columns:
    - Year Month Day Hours Minutes in YYYY
    - MM
    - DD
    - HH24
    - MI format in Local time
There are often three different sets of these five time columns in one file, each with different time formats (Local Time, Local Standard Time or UTC). The last of the five columns is named accordingly

This program converts these headers to more sensible ones:
    - YYYY-<time-format-tag>
    - MM-<time-format-tag>
    - DD-<time-format-tag>
    - HH-<time-format-tag>
    - MI-<time-format-tag>
where <time-format-tag> flags what time format the column is using:
    UTC - Universal Coordinated Time
    LTM - Local Time
    LST - Local Standard Time
    UNK - Unknown

"""

import os
import pandas as pd

def convert_headers(source, dest):
    df = pd.read_csv(source, low_memory=False)
    headers = list(df)

    col = 0
    for header in headers:
        if 'Year Month Day Hours' in header:
            # we have found the first of five
            # date columns. Figure out what
            # kind of time format it is
            tmp = headers[col+4].lower()
            if 'local time' in tmp:
                # time format is local time
                tag = "-LTM"
            elif 'local standard time' in tmp:
                tag = "-LST"
            elif 'universal coordinated time' in tmp:
                tag = "-UTC"
            else:
                # default tag is unknown
                tag = "-UNK"
            # change the headers
            headers[col] = "YYYY"+tag
            headers[col+1] = "MM"+tag
            headers[col+2] = "DD"+tag
            headers[col+3] = "HH"+tag
            headers[col+4] = "MI"+tag
        col += 1

    df.columns = headers
    df.to_csv(dest, index=False)

def processStation(source, dest, overwrite=False):

    if not os.path.isdir(dest):
        os.mkdir(dest)

    file_names = os.listdir(source)
    file_names = [x for x in file_names if '.txt' in x]

    i=0
    for name in file_names:
        perc = int((i/len(file_names))*100)
        print(str(perc)+'% | Fixing headers in', name, end='\r')
        path = os.path.normpath(os.path.join(source, name))
        newname = name[:-4]+'.csv'
        newpath = os.path.normpath(os.path.join(dest, newname))
        if not os.path.isfile(newpath) or overwrite:
            convert_headers(path, newpath)
        i+=1

    print('\nFinished')

import glob
station_folders = []

for f in glob.glob('D:/Datasets/BOM RAW/*/', recursive=False):
    source_folder = f
    target_folder = 'D:/Datasets/BOM RAW/fixed_header/' + f[-7:] 
    station_folders.append([source_folder, target_folder])

for station_folder in station_folders:
    dest = station_folder[1]
    print(dest)
    processStation(station_folder[0], dest)
