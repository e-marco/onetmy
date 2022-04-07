import pandas as pd
import logging
import validation
import calendar
import fs_stats

from config_parse import CONFIG

def month(data):
	"""
	Decides which month to use from a
	dictionary of months of the same
	calendar month (e.g. all February)
	Returns the key for the month
	"""

	calendar_month = list(data.keys())[0].strftime('%B')
	logging.info('Choosing representative '+calendar_month)

    # test variables and ranking currently only hard-coded
	#test_variables = ['mean-dni', 'mean-ghi', 'air-temp', 'relative-humidity'] # update 06/04/2022 following other publications weighting only based on dni / ghi#
    #variable_weightings = [0.75, 0.25, 0.0, 0.0] # update 06/04/2022
    #sort_by_windspeed = True # should make this an external input variable
    #sort_by_least_number_missing_days = True # will potentially override windspeed sorting

	test_variables = CONFIG['tmy']['variables']
	variable_weightings = CONFIG['tmy']['weighting']
	sort_by_windspeed = CONFIG['tmy']['sort-by-windspeed']
	sort_by_least_number_missing_days = CONFIG['tmy']['sort-by-least-number-missing-days']

	# Make the master CDF
	dfs = list(data.values())
	master = pd.concat(dfs, sort=False)
	master = fs_stats.createCDF(master)

	# Score the months
	fs_scores = []
	for month in data:
		df = data[month]

		# Create CDF for this month
		df = fs_stats.createCDF(df)

		# Calculate FS statistic for each
		# test variables (DNI, GHI, temp and humidity)
        # with respective weighting
		# For each month, the results are put in
		# a list with the month key:
		# [month, score]
		tmp = []
		
		cum_score = 0
		for idx,tv in enumerate(test_variables):
			cum_score += fs_stats.calculateFS(master[tv], df[tv]) * variable_weightings[idx]
        
		fs_scores.append([month, cum_score])

	# Rank all months based on their fs scores
	# (lowest wins, first sorted on test variable 1,
	# then 2, and so on)
	ranked_keys = sorted(fs_scores, key=lambda x: (x[1]))
	candidates = [x[0] for x in ranked_keys][:3]   # Keys for the best 3
	candidates_top_five = [x[0] for x in ranked_keys][:6]   # Keys for the best 6

	logging.debug('Candidates: '+str(candidates))
	logging.debug('candidates_top_five: '+str(candidates_top_five))

	# Remove all dfs apart from the candidates
	tmp = {}
	for key in candidates:
		tmp[key] = data[key]
	
	tmp_top_five = {}
	for key in candidates_top_five:
		tmp_top_five[key] = data[key]
		
	data = tmp
	data_top_five = tmp_top_five

	if sort_by_windspeed:
		logging.debug("Sorting by wind-speed")
        # The 3 months with the best ranking undergo one
        # more selection step: winner has the smallest
        # deviation in average monthly windspeed
		try:
			lt_average = master['wind-speed'].mean()
			deviances = {}
			for key in data_top_five:
				x = data_top_five[key]['wind-speed'].mean()
				x = abs(x-lt_average)
				deviances[key] = x

			extented_candidates = sorted(deviances, key=lambda x: deviances[x])
            
			deviances = {}
			for key in data:
				x = data[key]['wind-speed'].mean()
				x = abs(x-lt_average)
				deviances[key] = x

			ranked_candidates = sorted(deviances, key=lambda x: deviances[x])
            
			logging.debug('Winning candidate based on wind-speed: '+str(ranked_candidates[0]))
			logging.debug('Ranked candidates based on wind-speed: '+str(ranked_candidates))
		except KeyError:
			ranked_candidates = candidates
			extented_candidates = candidates_top_five
	else:
		ranked_candidates = candidates
		extented_candidates = candidates_top_five
    
	if sort_by_least_number_missing_days:
		logging.debug("Sorting by least number of missing days")
        # ranking for best three candidates based on least number of days with gaps
		number_of_gaps_per_candidate = count_gap_days(data, ranked_candidates)
		ranked_candidates = sorted(number_of_gaps_per_candidate, key=lambda x: number_of_gaps_per_candidate[x])
	
	logging.info('Winning candidate: '+str(ranked_candidates[0]))
	logging.debug('Ranked candidates: '+str(ranked_candidates))
	return ranked_candidates, extented_candidates

def count_gap_days(data, ranked_candidates):
	"""
	Counts number of days with any gaps remaining in the winning
	
	Returns the number of days for each ranked_candidate

	data - dict, keys are datetime objects and
		values are dataframes
	ranked_candidates - list of candidates, ordered
		by score (i.e. winning month is first entry)
	"""

	logging.debug('Counting days with any remaining gaps')
	
	number_of_gaps_per_candidate = {}
	month=list(data.keys())[0].month
	year=list(data.keys())[0].year
	eomday = calendar.monthrange(year, month)[1]
	
	for current_candidate in ranked_candidates:
		odf = data[current_candidate]	 # other dataframe
		number_of_gaps = 0
		
		for day in range(1, eomday+1):
			replacement_keys = [k for k in list(odf.index) if k.month==month and k.day==day]
			replacement_day = odf.loc[replacement_keys]
			
			
			if replacement_day.isnull().values.any():
				# There are empty values in the
				# day.
				number_of_gaps = number_of_gaps + 1
		
		logging.debug('Number of days with gaps for '+str(current_candidate)+': '+str(number_of_gaps))
		number_of_gaps_per_candidate[current_candidate] = number_of_gaps
		
	return number_of_gaps_per_candidate