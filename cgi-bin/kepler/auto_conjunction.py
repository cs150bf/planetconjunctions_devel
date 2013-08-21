#import matplotlib.dates as dates
#import datetime
#
#execfile('planet_conj.py')
#execfile('conj_funcs.py')
#execfile('planet_categorize.py')
#execfile('planet_d_r_comparison.py')
#execfile('conj_stats_funcs.py')

#utc_now = datetime.datetime.utcnow()
#jd_now = dates.num2julian(dates.date2num(utc_now))
#start_time = jd_now
#end_time = jd_now + 1
#time_step = 0.0001
#dps_mode = '1'
#r_mode = '1'
#conjunction_crit = 'stellar'
#datafile_formats = ['txt']
#date_format = 'utc'
#sort_method = ['time', 'sys_id']
#datafile_dir = '/tmp/kepler/'
#fn_head = 'local_test'
#verbose = True

def auto_conjunction(start_time, end_time, time_step, \
		dps_mode, r_mode, conjunction_crit, \
		datafile_formats, date_format, sort_method, \
		datafile_dir, fn_head, verbose):
	n_time_points = (end_time - start_time)/time_step
	if n_time_points > 1000000:
	    sys_start = range(0, 2000, 10)
        else:
	    sys_start = range(0, 2000, 50)
	pickle_file = 'pickle' in datafile_formats
	conjunction_fn_collection = []
	sys_conj_time_dict ={}
	acc_n_conjunctions = 0
	for i in range(0, len(sys_start)-1):
		sys_conj_time, acc_n_conjunctions, conj_time_file_name, \
			dps_mode, r_mode, conjunction_crit, \
			start_time, end_time = planet_conj(sys_start[i], sys_start[i+1], \
						start_time = start_time, n_time_points = n_time_points, time_step = time_step,\
						dps_mode = dps_mode, radius_mode = r_mode, \
						acc_n_conjunctions = acc_n_conjunctions, df_dir=datafile_dir, verbose = verbose)
		#conjunction_fn_collection.append(conj_time_file_name)
		#if 'sys_id' in sort_method:
		sys_conj_time_dict.update(sys_conj_time)
		#if i==0:
		#	to_append = False
		#else:
		#	to_append = True
		#conj_time_save_to_file(fn_head, sys_conj_time, \
                #                        r_mode, dps_mode, conjunction_crit,\
                #                        start_time, end_time, date_format=date_format, \
		#			pickle_file = pickle_file, to_append = to_append)
	fns = []
	if 'sys_id' in sort_method:
		filenames = conj_time_save_to_file(datafile_dir+fn_head, sys_conj_time_dict, \
					r_mode, dps_mode, conjunction_crit, \
					start_time, end_time, date_format=date_format, \
					pickle_file=pickle_file, to_append=False)
		fns.extend(filenames)
	if 'time' in sort_method:
		#conj_timeline_dict = conjunction_datafiles_timeline_sort([datafile_dir+x for x in conjunction_fn_collection], verbose=verbose)		
		conj_timeline_dict = conjunction_system_timeline_sort({}, sys_conj_time_dict, start_time, end_time)
		filenames = conj_timeline_printout(datafile_dir+fn_head+'_timeline', \
				conj_timeline_dict, start_time, end_time, date_format=date_format, pickle_file=pickle_file)
		fns.extend(filenames)
	return acc_n_conjunctions, fns

#n_conjunctions, fns = auto_conjunction(start_time, end_time, time_step, \
#		dps_mode, r_mode, conjunction_crit, \
#		datafile_formats, date_format, sort_method, \
#		datafile_dir, fn_head, verbose)
	
