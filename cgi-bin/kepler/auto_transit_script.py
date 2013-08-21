#!/opt/vegas/bin/python2.6
import os, sys
os.environ['HOME']='/tmp/'
os.environ['MPLCONFIGDIR']='/tmp/'
import matplotlib.dates as dates
import pydoc, datetime, string, pickle

log_file = open('/tmp/kepler/log.txt', 'w')
log_file.write('Hello world!\n')
log_file.close()
	
"""
#execfile('test_funcs.py')
execfile('transit_funcs.py')
execfile('auto_transit.py')
execfile('planet_transit.py')
execfile('transit_stats_funcs.py')
execfile('transit_stats.py')
execfile('planet_categorize.py')
execfile('planet_d_r_comparison.py')
"""

#def auto_transit(start_time, end_time, time_step, \
#		dps_mode, r_mode, transit_crit, \
#		datafile_formats, date_format, sort_method, \
#		datafile_dir, fn_head, verbose):
def update_tasks_list(submitted_task_id='', task_type='submitted'):
    """
    submitted_tasks.pickle=
			{'n_tasks': INTEGER,
			 'task_1': {'type':submitted, 
					'event_time': <time>, 
					'fn_head': STRING, 
					'start_time': FLOAT, ...
					},
			 'task_2': {}, ...
    """
    event_time = str(datetime.datetime.utcnow())
    #with open('count_'+task_type+'.txt', 'r+') as count_file:
    #    n_task_count = int(count_file.readline())
    with open(datafile_dir + task_type + '_tasks.pickle', 'r') as tasks_pickle:
        tasks_dict = pickle.load(tasks_pickle)
    new_task, tasks_dict = update_task_dict(tasks_dict, event_time, submitted_task_id, task_type=task_type)
    with open(datafile_dir + task_type + '_tasks.pickle', 'w') as tasks_pickle:
        pickle.dump(tasks_dict, tasks_pickle)
    with open(datafile_dir + task_type + '_tasks.txt', 'r+') as tasks_txt:
        old = tasks_txt.read()
	old_2line_on = old[old.find('\n')+1:]
        tasks_txt.seek(0)
        newline = 'The number of ' + task_type + ' tasks is : ' + str(tasks_dict['n_tasks']) + '\n'
        tasks_txt.write(newline + old_2line_on)
    with open(datafile_dir + task_type + '_tasks.txt', 'a+b') as tasks_txt:
        update_tasks_txt(new_task, tasks_txt, task_type)
    return new_task['task_id'] 
 
def update_task_dict(tasks_dict, event_time, submitted_task_id='', task_type='submitted'):
    n_tasks = tasks_dict['n_tasks']
    if task_type == 'submitted':
        new_task_id = 'task_'+str(n_tasks+1)
    else:
        new_task_id = submitted_task_id
    tasks_dict['n_tasks'] = n_tasks+1
    new_task = {'task_id':new_task_id, 'type': task_type,  'event_time':event_time}
    new_task['start_time'] = start_time
    new_task['end_time'] = end_time
    new_task['time_step'] = time_step
    new_task['transit_crit'] = transit_crit
    new_task['dps_mode'] = dps_mode
    new_task['r_mode'] = r_mode
    new_task['datafile_formats'] = datafile_formats
    new_task['date_format'] = date_format
    new_task['sort_method'] = sort_method
    new_task['fn_head'] = fn_head
    new_task['verbose'] = verbose
    if task_type == 'completed':
        new_task['output_files_dir'] = datafile_dir+fn_head+'*'
        new_task['n_conjunctions'] = n_conjunctions
    tasks_dict[new_task_id] = new_task
    return new_task, tasks_dict
    
def update_tasks_txt(new_task_dict, tasks_txt_file, task_type):
    tasks_txt_file.write('-------------------------------------------------\n')
    tasks_txt_file.write('task id: '+new_task_dict['task_id']+'\n')
    tasks_txt_file.write('task type: '+new_task_dict['type']+'\n')
    tasks_txt_file.write(task_type+' time: '+new_task_dict['event_time']+'\n')
    listed_keys = ['start_time', 'end_time', 'time_step', \
		 'transit_crit', 'dps_mode', 'r_mode', \
		 'datafile_formats', 'date_format', 'sort_method',\
		 'fn_head', 'verbose']
    for key in listed_keys:
        if new_task_dict.has_key(key):
            tasks_txt_file.write('\t'+key+' : '+str(new_task_dict[key])+'\n')
    if task_type == 'completed':
        tasks_txt_file.write('A total number of '+str(new_task_dict['n_conjunctions'])+' conjunctions have occurred.\n')
        tasks_txt_file.write('Output files can be found at: '+new_task_dict['output_files_dir']+'\n')
    tasks_txt_file.write('-------------------------------------------------\n')
 
def main(argv):
	start_time=argv[0]
	end_time = argv[1]
	time_step = argv[2]
	dps_mode = '1'
	r_mode = '1'
	transit_crit = argv[3]
	datafile_formats = argv[4]
	date_format = argv[5]
	sort_method = argv[6]
	datafile_dir = argv[7]
	fn_head = argv[8]
	verbose = argv[9]
	task_id = argv[10]
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
	if 'sys_id' in sort_method:
		transit_time_save_to_file(datafile_dir+fn_head, sys_transit_time_dict, \
					r_mode, dps_mode, transit_crit, \
					start_time, end_time, date_format=date_format, \
					pickle_file=pickle_file, to_append=False)
	if 'time' in sort_method:
		#transit_timeline_dict = transit_datafiles_timeline_sort([datafile_dir+x for x in transit_fn_collection], verbose=verbose)		
		transit_timeline_dict = transit_system_timeline_sort({}, sys_transit_time_dict)
		transit_timeline_printout(datafile_dir+fn_head+'_timeline', transit_timeline_dict, date_format=date_format, pickle_file=pickle_file)
	task_id = update_tasks_list(task_id, task_type='completed')

if __name__=="__main__":
	log_file = open('/tmp/kepler/log.txt', 'w')
	log_file.write('Hello world!\n')
	log_file.close()
	main(sys.argv[1:])
