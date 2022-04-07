import datetime
from pvlib import solarposition
import pytz
import pandas as pd
from math import cos, radians
import logging

from config_parse import CONFIG

def remedy(x, lat, lon, zenith_limit):
	"""
	Logical filling function that is applied to
	a dataframe using the 'apply' function

	The dataframe needs to contain **only** the
	following columns:
	mean-dhi, mean-dni, mean-ghi
	Its name needs to be the timezone-aware time
	at which the readings were taken (datetime)

	zenith_limit is the zenith angle at which
	it is considered night time
	"""

	if x.isnull().values.any():
		# There are missing values

		tmp = x.isnull()
		t = x.name	# Time of this row

		solpos = solarposition.get_solarposition(t, lat, lon)
		z = solpos['zenith'].values

		if z>zenith_limit:
			# It's night time. Fill with zeros
			x.values[:] = 0
		elif tmp.sum()==1:
			# Only one is missing. Determine
			# the missing value algebraically
			if not tmp['mean-ghi']:
				# GHI is missing
				x['mean-ghi'] = x['mean-dni']*cos(radians(z)) + x['mean-dhi']
			elif not tmp['mean-dni']:
				# DNI is missing
				x['mean-dni'] = (x['mean-ghi']-x['mean-dhi'])/cos(radians(z))
			else:
				# DHI is missing
				x['mean-dhi'] = x['mean-ghi'] - x['mean-dni']*cos(radians(z))
	return x

def logicalfill(df, lat, lon, zenith_limit=96):
	"""
	'Logically fills' a dataframe's
	irradiance columns. Does this inplace
	"""

	df[['mean-ghi', 'mean-dni', 'mean-dhi']].apply(remedy, axis=1, lat=lat, lon=lon, zenith_limit=zenith_limit)

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
	logicalfill(df, lat, lon)

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
