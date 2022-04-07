import tmy
import fs_stats
import os
import pandas as pd
import datetime
import logging
import validation
import load
import fill
import sys

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logging.info('Loading files')

data = {}

dir = '/media/jack/extssd/BoM_2018/'
station = '072150'

files = [x for x in os.listdir(dir) if (station in x and '.pkl' in x)]

for file in files:
    year = int(file[7:9])+2000
    month = int(file[10:12])
    path = dir+file
    df = pd.read_pickle(path)
    key = datetime.datetime(year, month, 1)
    data[key] = df

#for i in range(1, 13):
#    name = station+month.strftime("_%y_%m")
#    path = os.path.normpath(dir+name+'.pkl')
#    df = pd.read_pickle(path)
#    key = list(df.index)[0]
#    data[key] = df

print(data)
