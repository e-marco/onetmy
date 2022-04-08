import datetime
from pvlib import solarposition
import pytz
import pandas as pd
import numpy as np
import logging

from config_parse import CONFIG

def logicalfill(df, lat, lon, zenith_limit=96):
	"""
	'Logically fills' a dataframe's
	irradiance columns. Does this inplace
	"""

	#df[['mean-ghi', 'mean-dni', 'mean-dhi']].apply(remedy, axis=1, lat=lat, lon=lon, zenith_limit=zenith_limit)
	solpos = solarposition.get_solarposition(df.index, lat, lon)
	
	logging.debug("Number of invalid values: {}".format(df.isna()[['mean-ghi', 'mean-dni', 'mean-dhi']].sum()))
	
	data_filter = (df.isna()['mean-ghi']) & (df.notna()['mean-dni']) & (df.notna()['mean-dhi'])
	df.loc[data_filter,'mean-ghi'] = df[data_filter]['mean-dni']*np.cos(np.deg2rad(solpos['zenith'])) + df[data_filter]['mean-dhi']
	logging.debug("Number of invalid values after GHI fill: {}".format((df.isna()[['mean-ghi', 'mean-dni', 'mean-dhi']].sum())))
	
	data_filter = (df.isna()['mean-dni']) & (df.notna()['mean-ghi']) & (df.notna()['mean-dhi'])
	df.loc[data_filter,'mean-dni'] = (df[data_filter]['mean-ghi']-df[data_filter]['mean-dhi'])/np.cos(np.deg2rad(solpos['zenith']))
	logging.debug("Number of invalid values after DNI fill: {}".format(df.isna()[['mean-ghi', 'mean-dni', 'mean-dhi']].sum()))
	
	data_filter = (df.isna()['mean-dhi']) & (df.notna()['mean-ghi']) & (df.notna()['mean-dni'])
	df.loc[data_filter,'mean-dhi'] = df[data_filter]['mean-ghi'] - df[data_filter]['mean-dni']*np.cos(np.deg2rad(solpos['zenith']))
	logging.debug("Number of invalid values after DHI fill: {}".format(df.isna()[['mean-ghi', 'mean-dni', 'mean-dhi']].sum()))
	
	data_filter = solpos['zenith'] > zenith_limit
	df.loc[data_filter,'mean-ghi'] = 0
	df.loc[data_filter,'mean-dni'] = 0
	df.loc[data_filter,'mean-dhi'] = 0
	logging.debug("Number of invalid values after zenith_limit fill: {}".format(df.isna()[['mean-ghi', 'mean-dni', 'mean-dhi']].sum()))
	return df

def fill(df, station, data_requirement=0.9):
	"""
	Logical fills the given dataframe, then
	interpolates gaps less than an hour
	Returns True if the procedure was successful,
	False otherwise
	"""

	lon = CONFIG['stations'][station]['longitude']
	lat = CONFIG['stations'][station]['latitude']

	#logging.debug('Filling gaps')

	# Logical fill the solar columns
	logging.debug('Logical filling')
	df = logicalfill(df, lat, lon)

	# If the percentage of missing data is
	# unacceptable, quit now
	perc_missing = df.isnull().sum()/len(df)
	perc_missing = perc_missing.mean()
	logging.debug('Logical filling complete. Percentage of data missing: '+str(perc_missing))
	if 1-perc_missing<data_requirement:
		logging.warning('Available data requirement ('+str(data_requirement)+') not met')
		return False

	# Interpolate column gaps of up to 60 minutes
	logging.debug('Interpolating small gaps')
	df.interpolate(axis=0, limit=60, inplace=True)
	
	perc_missing = df.isnull().sum()/len(df)
	perc_missing = perc_missing.mean()
	logging.debug('Interpolation complete. Percentage of data missing: '+str(perc_missing))
	return True


if __name__=='__main__':
	df = pd.read_pickle('loadme')
	lat = -35.2012398
	lon = 149.0511168
	before = df.isnull().sum()/len(df)
	logicalfill(df, lat, lon)
	after = df.isnull().sum()/len(df)
	print(before-after)
