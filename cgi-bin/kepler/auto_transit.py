def auto_transit(start_time, end_time, time_step, \
		dps_mode, r_mode, transit_crit, \
		datafile_formats, date_format, sort_method, \
		datafile_dir, fn_head, verbose):
	n_time_points = (end_time - start_time)/time_step
	if n_time_points > 1000000:
	    sys_start = range(0, 2000, 10)
        else:
	    sys_start = range(0, 2000, 50)
	pickle_file = 'pickle' in datafile_formats
	transit_fn_collection = []
	sys_transit_time_dict ={}
	acc_n_conjunctions = 0
	for i in range(0, size(sys_start)-1):
		sys_transit_time, acc_n_conjunctions, transit_time_file_name, \
			dps_mode, r_mode, transit_crit, \
			start_time, end_time = planet_transit(sys_start[i], sys_start[i+1], \
						start_time = start_time, n_time_points = n_time_points, time_step = time_step,\
						dps_mode = dps_mode, radius_mode = r_mode, \
						acc_n_conjunctions = acc_n_conjunctions, df_dir=datafile_dir, verbose = verbose)
		#transit_fn_collection.append(transit_time_file_name)
		#if 'sys_id' in sort_method:
		sys_transit_time_dict.update(sys_transit_time)
		#if i==0:
		#	to_append = False
		#else:
		#	to_append = True
		#transit_time_save_to_file(fn_head, sys_transit_time, \
                #                        r_mode, dps_mode, transit_crit,\
                #                        start_time, end_time, date_format=date_format, \
		#			pickle_file = pickle_file, to_append = to_append)
	fns = []
	if 'sys_id' in sort_method:
		filenames = transit_time_save_to_file(datafile_dir+fn_head, sys_transit_time_dict, \
					r_mode, dps_mode, transit_crit, \
					start_time, end_time, date_format=date_format, \
					pickle_file=pickle_file, to_append=False)
		fns.extend(filenames)
	if 'time' in sort_method:
		#transit_timeline_dict = transit_datafiles_timeline_sort([datafile_dir+x for x in transit_fn_collection], verbose=verbose)		
		transit_timeline_dict = transit_system_timeline_sort({}, sys_transit_time_dict)
		filenames = transit_timeline_printout(datafile_dir+fn_head+'_timeline', \
				transit_timeline_dict, date_format=date_format, pickle_file=pickle_file)
		fns.extend(filenames)
	return acc_n_conjunctions, fns

