import pandas as pd
import numpy as np
import datetime
import logging
import calendar

def makeSortColumn(x):
	t = x['datetime']
	x['sort-score'] = (t.day*24 + t.hour)*60 + t.minute
	return x

def fillRemainingGaps(data, ranked_candidates, extented_candidates):
	"""
	Replaces any gaps remaining in the winning
	dataframe with days from other well-scoring
	months
	Returns the key and dataframe of the winning
	month

	data - dict, keys are datetime objects and
		values are dataframes
	ranked_candidates - list of candidates, ordered
		by score (i.e. winning month is first entry)
	"""

	logging.info('Replacing any remaining gaps...')

	wkey = ranked_candidates[0]	 # winning key
	wdf = data[wkey]				# winning dataframe
	other_candidates = ranked_candidates[1:]

	# Loop through the index of the winning
	# dataframe, which is a heap of datetime
	# objects
	timestamps = list(wdf.index)
	month = timestamps[0].month
	year=timestamps[0].year
	eomday = calendar.monthrange(year, month)[1]
	#for i in range(0, len(timestamps)):
	for day in range(1, eomday+1):
		source_keys = [k for k in list(wdf.index) if k.month==month and k.day==day]
		source_day = wdf.loc[source_keys]
		source_shape = source_day.shape
		# If there is a Nan anywhere in this
		# row, replace this day
		try:
			missing_data = source_day.isnull().values.any()
		except IndexError:
			# The number of rows has changed
			# Complain and break
			logging.error('Unexpected end of dataframe (the\
				number of rows in this dataframe has changed)')
			break
		if missing_data:
			logging.info('Replacing '+str(list(source_day.index)[0]))
			#month = timestamps[i].month
			#day = timestamps[i].day

			# Go through each other candidate and get
			# the same day. If there's no missing values
			# in that day, quit the loop and use it as
			# the replacement day
			replacement_day = None
			replacement_found = False
			for other_candidate in other_candidates:
				odf = data[other_candidate]	 # other dataframe
				replacement_keys = [k for k in list(odf.index) if k.month==month and k.day==day]
				replacement_day = odf.loc[replacement_keys]
				replacement_day_shape = replacement_day.shape

				if (not replacement_day.isnull().values.any()) and (replacement_day_shape == source_shape):
					# There are no empty values in the
					# replacement day. We have fixed this
					# gap
					logging.debug('Taking day from '+str(list(replacement_day.index)[0]))
					replacement_found = True
					break
			# If not found, go through extended list of five candidates
			if not replacement_found:
				logging.debug('Using extended candidate list')
				replacement_day = None
				replacement_found = False
				for other_candidate in extented_candidates:
					odf = data[other_candidate]	 # other dataframe
					replacement_keys = [k for k in list(odf.index) if k.month==month and k.day==day]
					replacement_day = odf.loc[replacement_keys]

					if (not replacement_day.isnull().values.any()) and (replacement_day_shape == source_shape):
						# There are no empty values in the
						# replacement day. We have fixed this
						# gap
						logging.debug('Taking day from '+str(list(replacement_day.index)[0]))
						replacement_found = True
						break
			
			# If we couldn't find a replacement, we have to
			# quit processing of the entire station!
			if not replacement_found:
				logging.error('Failed to replace missing data in winning month')
				break

			# REPLACE DAY
			# Remove the old day
			#keys_to_replace = [k for k in list(wdf.index) if k.month==month and k.day==day]
			
			wdf.loc[source_keys] = replacement_day.values
			
			## old code
			#wdf = wdf.drop(keys_to_replace)
			# Put in the new day
			#wdf = wdf.append(replacement_day)

			
			
			# Rows are out of order now. Sort
			# the dataframe based on day, hour
			# and minute, NOT on month (we have
			# different years)
			# Move the datetime out of the index
			#wdf.reset_index(inplace=True)
			# Create a column we can sort on
			#wdf = wdf.apply(makeSortColumn, axis=1)
			# Sort
			#wdf.sort_values(by='sort-score', inplace=True)
			# Delete sort column and restore index
			#del wdf['sort-score']
			#wdf.set_index('datetime', inplace=True)

	return wkey, wdf

def smooth(df, minutes):
	"""
	Linearly interpolates a certain number
	of minutes around two adjacent rows of
	data that are from different years
	Dataframe's index must be datetime
	Applies changes in place
	"""

	logging.info('Smoothing year interfaces')

	# Loop through the timestamps in the new
	# dataframe, and if the next timestamp is
	# of a different year, we need to smooth
	# that interface
	timestamps = df.index
	for i in range(0, len(timestamps)):
		t = timestamps[i]
		t_next = timestamps[(i+1)%len(timestamps)]
		if t.year!=t_next.year:

			# Calculate indicies for start and
			# end of the slice
			i0 = i-minutes
			i1 = (i+minutes)%len(timestamps)

			if i0<0:
				if i1>i0:
					# Start of slice wraps around
					# to end of df
					a = df.iloc[i0:]
					b = df.iloc[:i1]
					slice = pd.concat([a, b])
				else:
					raise RuntimeError('Unknown fault during smoothing')
			else:
				if i1<i0:
					# End of slice wraps around
					# to start of df
					a = df.iloc[i0:]
					b = df.iloc[:i1]
					slice = pd.concat([a, b])
				else:
					# Normal case
					slice = df.iloc[i0:i1]

			# Remove all but the first and last values
			slice.iloc[1:-1] = np.nan
			# Interpolate
			slice.interpolate(inplace=True)
			# Put back in dataframe
			df.update(slice, overwrite=True)
