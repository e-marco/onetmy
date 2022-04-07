import logging
import os
import pandas as pd

def merge(data):
	"""
	Merges the 12 chosen months to create
	the TMY. data is a dictionary with
	datetime.datetime keys and dataframe
	values
	Forces all data to be numeric
	"""

	logging.info('Merging months to create a single year')

	# Sort the dataframes into a list using
	# their datetime keys
	ordered_keys = sorted(data, key=lambda x: x.month)
	ordered_dfs = [data[k] for k in ordered_keys]

	# Merge them into one dataframe
	tmy_df = pd.concat(ordered_dfs)

	# Ensure all data is numeric
	logging.debug('Ensuring all data is numeric')
	for x in list(tmy_df):
		tmy_df[x] = pd.to_numeric(tmy_df[x], errors='coerce')

	return tmy_df

def to_csv(df, outpath):
	"""
	Exports the dataframe to .csv
	"""

	logging.info('Exporting to '+outpath)

	# If the directory doesn't exist, make it
	dir = os.path.dirname(outpath)
	if dir and not os.path.isdir(dir):
		os.mkdir(dir)

	# Export the file
	df.to_csv(outpath)

def to_csv_no_index(df, outpath):
	"""
	Exports the dataframe to .csv
	"""

	logging.info('Exporting to '+outpath)

	# If the directory doesn't exist, make it
	dir = os.path.dirname(outpath)
	if dir and not os.path.isdir(dir):
		os.mkdir(dir)

	# Export the file
	df.to_csv(outpath, index=False)