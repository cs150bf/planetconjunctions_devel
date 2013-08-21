execfile('./kepler/auto_transit.py')
execfile('./kepler/planet_transit.py')
execfile('./kepler/transit_funcs.py')
execfile('./kepler/transit_stats_funcs.py')
execfile('./kepler/transit_stats.py')
execfile('./kepler/planet_categorize.py')
execfile('./kepler/planet_d_r_comparison.py')

datafile_dir ='/tmp/'
start_time = 2454900.0
end_time = 2454901.0
time_step = 1.0/100000
dps_mode = '1'
r_mode = '1'
transit_crit = 'stellar'
datafile_formats = ['txt', 'pickle']
date_format = 'utc'
sort_method = ['sys_id', 'timeline']
fn_head = 'kpler_test_datafile'
verbose=False

auto_transit(start_time, end_time, time_step, \
		dps_mode, r_mode, transit_crit, \
		datafile_formats, date_format, sort_method, \
		datafile_dir, fn_head, verbose)
	
