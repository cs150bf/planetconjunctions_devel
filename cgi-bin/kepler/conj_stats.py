from numpy import *
from scipy import *
from itertools import *
import pickle
import pylab

#execfile('conjunction_stats_funcs.py')

def conjunction_stats(filename_list = [], acc_time_per = 1.0, \
			dps_mode = '1', r_mode = '1',\
			 start_time = 2456069.0, end_time = 2456169.0, verbose = False):
	"""
	"""

	dps_cp = dps_mode
	r_cp = r_mode
	if r_mode == '1' or r_mode == 'default':
		r_mode = '1) Rad: Planet radius'
	elif r_mode == '2':
		r_mode = '2) (r/R*)xRad2: (ratio of planet radius to stellar radius)*(stellar radius)'
	else:
		r_mode = '1) Rad: Planet radius' # default

	if dps_mode == '1' or dps_mode == 'default':
		dps_mode = '1) a: Semi-major axis of the orbit'
	elif dps_mode == '2':
		dps_mode = '2) (d/R*)xRad2: (ratio of planet-star separation to stellar radius)*(stellar radius)'
	else:
		dps_mode = '1) a: Semi-major axis of the orbit' # default


	acc_dict = {0:0}
	combined_conjunction_stats_dict = {'init':0}
	max_max_n_planets = 2
	for filename in filename_list:
		sys_conjunction_time = conjunction_time_readin(filename, verbose)
		max_n_planets = 2
		for sys_id in sys_conjunction_time.keys():
			if max_n_planets < sys_conjunction_time[sys_id]['n_planets']:
				max_n_planets = sys_conjunction_time[sys_id]['n_planets']
			if max_max_n_planets < sys_conjunction_time[sys_id]['n_planets']:
				max_max_n_planets = sys_conjunction_time[sys_id]['n_planets']

		if verbose:
			print 'Max number of planets in a single system :', max_n_planets
			print 'in current file :\n\t', filename
		for target_n_planets in range(2, max_n_planets+1):
			conjunction_stats_dict = conjunction_times_stats(sys_conjunction_time, target_n_planets, \
								acc_time_per, start_time, end_time, verbose)

			combined_conjunction_stats_dict = conjunction_stats_dict_update(combined_conjunction_stats_dict,\
										 conjunction_stats_dict, verbose)
			conjunction_n_stats_save_to_file(filename+'_stats_'+str(target_n_planets),\
						 conjunction_stats_dict, dps_mode, r_mode, pickle_file = True)
			acc_vec_tmp = conjunction_stats_dict['acc_vec']
			if acc_dict.has_key(target_n_planets):
				acc_vec_tmp = acc_vec_tmp + acc_dict[target_n_planets]
			if acc_dict.has_key('total'):
				acc_total = acc_dict['total']
				acc_total = acc_total + acc_vec_tmp
			else:
				acc_total = acc_vec_tmp
			acc_dict.update({target_n_planets: acc_vec_tmp, 'total':acc_total})

	conjunction_n_stats_save_to_file('conjunction_stats_all_systems_'+str(start_time)+'_to_'+str(end_time),\
					 combined_conjunction_stats_dict,  dps_mode, r_mode, pickle_file = True)

	colors_list = ['b', 'g', 'c', 'r', 'y']
	for i in range(2, max_max_n_planets+1):
		#pattern = raw_input('Please input plot pattern :')
		#color = raw_input('Please select plot color :')
		pattern = '^'
		color = colors_list[i-2]
		pobj, plegend = plot_conjunction_stats(target_n_planets = i, acc_vec = acc_dict[i], \
				t_vec = combined_conjunction_stats_dict['t_vec'],\
				acc_time_per = combined_conjunction_stats_dict['acc_time_per'], \
				pattern = pattern, color = color, stack = False, verbose = verbose)
		pylab.legend(tuple([pobj]), tuple([plegend]))
		pylab.xlabel('Time (BJD): '+str(start_time)+' to '+str(end_time))
		pylab.ylabel('Number of conjunctions per '+str(acc_time_per)+' day')
		pylab.title('Number of conjunctions of '+str(i)+' planets')
		pylab.savefig('conjunctions_'+str(i)+'p_per1day_2456069_2456169_all_sys_mode'+str(dps_cp)+str(r_cp)+'.svg')
		pylab.savefig('conjunctions_'+str(i)+'p_per1day_2456069_2456169_all_sys_mode'+str(dps_cp)+str(r_cp)+'.png')
		pylab.savefig('conjunctions_'+str(i)+'p_per1day_2456069_2456169_all_sys_mode'+str(dps_cp)+str(r_cp)+'.eps')
		pylab.savefig('conjunctions_'+str(i)+'p_per1day_2456069_2456169_all_sys_mode'+str(dps_cp)+str(r_cp)+'.ps')
		pylab.show()
	

	return acc_dict, combined_conjunction_stats_dict, max_max_n_planets
