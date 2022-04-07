import yaml
import logging
import logging.config
import os
import pandas as pd
import load
from config_parse import CONFIG
import fill
import filesearch
import validation
import tmy
import pytz

def processMonth(station, paths):
	"""
	Processes a calendar month (e.g. all Jan
	files) for a station. Returns the month key
	and month datafile for the month that needs
	to be put in the TMY (all processing complete)
	"""

	if len(paths)==0:
		logging.error('Path dictionary empty. \
		Quitting processing of this calendar month for station %s', station)
		return None, None

	calendar_month = list(paths.keys())[0].strftime('%B')

	# Data is a dictionary with keys that are
	# datetime.datetime objects, values that are
	# dataframes
	data = {}

	for month in paths:	# remember: month is a datetime object

		# Load any files associated with this particular month
		#logging.info('Loading...')
		df = load.load(paths[month], station, month.year, month.month)
		
		if df is None:
			logging.warning('Skipping this month')
			continue
		logging.info('Validation...')
		# Run some validation to check we should keep going
		validation.removePatchyColumns(df, 0.7)
		if not validation.requiredColumns(df):
			logging.warning('Required columns not present in dataframe. Skipping this month')
			continue
		logging.info('Fill gaps...')
		# Fill gaps (logical filling and plain interpolation)
		# This procedure checks the data requirement BETWEEN
		# logical filling and interpolation, as specified by
		# our theory. If we don't meet the requirement, quit
		# this month
		fill_success = fill.fill(df, station)
		if not fill_success: continue

		logging.info('Successful load of '+str(month))
		data[month] = df
		
		# exporting gap-filled data
		name = station+month.strftime("_%Y_%m")
		path = os.path.normpath(preprocesspath+'/'+name+'.csv')
		tmy.export.to_csv(df, path)

	# Check to see if we have enough of this
	# calendar month to continue. If we don't,
	# the TMY can't be made and we should quit
	# the processing of this month
	if not validation.month(list(data.keys()), 1):
		logging.error('Not enough data for this calendar month('+calendar_month+'). Quitting processing of station "'+station+'"')
		return None, None

	# Save data as a bunch of pickle files
	#for month in data:
	#	df = data[month]
	#	dir = '/media/jack/extssd/BoM_2018/'
	#	name = station+month.strftime("_%y_%m")
	#	path = os.path.normpath(dir+name+'.pkl')
	#	df.to_pickle(path)

	# This entire calendar month has been loaded.
	# Decide on which one we want in the TMY
	# (winner is first in the returned list)
	ranked_candidates, extented_candidates = tmy.decide.month(data)

	# Execute the final gap replace step on the
	# winner, using the other candidates as 'spare parts'
	winning_key, winning_df = tmy.polish.fillRemainingGaps(data, ranked_candidates, extented_candidates)
	
	if winning_df.isnull().values.any():
		logging.warning('TMY generation for %s of station %s still has some gaps.', calendar_month, station)
	logging.info('TMY generation for %s of station %s complete', calendar_month, station)

	return winning_key, winning_df



def processStation(station, source_dir, pattern, outpath):
	"""
	Creates the TMY for a station
	returns True or False if its successful

	station - name of the station (as defined
	in config.yml)
	source_dir - directory to search for data files
	pattern - regex pattern used to find files
	outpath - path for the output TMY file
	"""

	# Find files. If we didn't find any,
	# or if we don't have enough, quit
	try:
		paths = filesearch.run(source_dir, pattern)
	except FileNotFoundError:
		logging.warning(source_dir+' is not a directory. Skipping processing of this station')
		return False

	if not paths:
		logging.warning('No files found. Quitting processing of station "'+station+'"')
		return False

	dates = list(paths.keys())
	if not validation.months(dates, 10):
		logging.warning('Data requirement not satisfied. Quitting processing of station "'+station+'"')
		return False


	#subset = {}
	#for key in paths:
	#	if key.month==1 and key.year>2003 and key.year<2008:
	#		subset[key] = paths[key]
	#paths = subset


	# Load and gap fill the files
	logging.info('Starting load process')
	tmy_months = {}

	# Loop through each calendar month. This
	# allows you to decide on which one you
	# want in the TMY at the end of the loop,
	# and dump any unnecessary data at the same
	# time
	for month_no in range(1, 13):

		# Create a subset of the paths dictionary
		# The subset only has path lists for files
		# of a specific calendar month
		paths_subset = {}
		for key in paths:
			if key.month==month_no:
				paths_subset[key] = paths[key]

		# Process this calendar month. Put the
		# winning month in the TMY dictionary
		winning_key, winning_df = processMonth(station, paths_subset)
		if winning_key is None:
			# Processing month failed
			# Quit processing of station
			return False
		tmy_months[winning_key] = winning_df

	# Join all of those datafiles
	df = tmy.export.merge(tmy_months)

	# Smooth interfaces between different years
	tmy.polish.smooth(df, 4*60)

	if df.isnull().values.any():
		logging.warning('Dataset still contains gaps! Please check!!')
	else:
		# Export to a file
		tmy.export.to_csv(df, outpath)
		
		apply_offset = CONFIG['stations'][station]['apply_offset']
		offset = CONFIG['stations'][station]['offset']
		if offset!=apply_offset:
			df = df.tz_convert(pytz.FixedOffset(apply_offset))
			
		df.reset_index(inplace=True)
		df['Year'] = pd.DatetimeIndex(df['datetime']).year
		df['Month'] = pd.DatetimeIndex(df['datetime']).month
		df['Day'] = pd.DatetimeIndex(df['datetime']).day
		df['Hour'] = pd.DatetimeIndex(df['datetime']).hour
		df['Minute (Local Standard Time)'] = pd.DatetimeIndex(df['datetime']).minute
		del df['datetime']
		df.rename(columns = {'precip':'Precipitation since last (AWS) observation in mm', 
							  'air-temp':'Air Temperature in degrees Celsius', 
							  'wet-bulb':'Wet bulb temperature in degrees Celsius', 
							  'dew-point':'Dew point temperature in degrees Celsius', 
							  'relative-humidity':'Relative humidity in percentage %', 
							  'wind-speed':'Wind (1 minute) speed in km/h', 
							  'wind-direction':'Wind (1 minute) direction in degrees true', 
							  'station-level-pressure':'Station level pressure in hPa', 
							  'mean-ghi':'Mean global horizontal irradiance (over 1 minute) in W/sq m', 
							  'mean-dni':'Mean direct normal irradiance (over 1 minute) in W/sq m', 
							  'mean-dhi':'Mean diffuse horizontal irradiance (over 1 minute) in W/sq m'}, inplace = True) 
		cols = df.columns.tolist()
		cols = cols[-1:] + cols[:-1]
		cols = cols[-1:] + cols[:-1]
		cols = cols[-1:] + cols[:-1]
		cols = cols[-1:] + cols[:-1]
		cols = cols[-1:] + cols[:-1]
		df = df[cols]
		
		tmy.export.to_csv_no_index(df, outpath.replace(".csv","_formattedHeader.csv"))
	return True



# Set up logger
with open('logconfig.yml', 'r') as f:
	logconfig = yaml.safe_load(f.read())
	logging.config.dictConfig(logconfig)

for station_name in CONFIG['stations']:
	logging.info('Processing station "'+station_name+'"')

	station_info = CONFIG['stations'][station_name]
	indir = os.path.normpath(CONFIG['folders']['source'] + '/' + station_name + '/')
	pattern = CONFIG['folders']['pattern']
	outpath = os.path.normpath(CONFIG['folders']['destination-tmy'].format(station_name))
	preprocesspath = os.path.normpath(CONFIG['folders']['destination-filtered'] + '/' + station_name + '/')

	q = processStation(station_name, indir, pattern, outpath)

	tmp = 'Processing of station "'+station_name+'"'
	if q: logging.info(tmp+' was successful')
	else: logging.info(tmp+' failed')