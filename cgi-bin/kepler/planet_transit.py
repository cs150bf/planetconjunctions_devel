from scipy.io.idl import readsav
from numpy import *
import pickle


def planet_transit(n_system_start = 0, n_system_end = 5, start_time = 2456518.0, \
			n_time_points = 300000.0, time_step = 1.0/100000.0, \
			dps_mode = '1', radius_mode = '1', transit_crit = 'stellar', \
			acc_n_conjunctions=0, df_dir='./', save_to_file=False, verbose = False):
	"""	
	- n_system_start: int 	(>0)
	- n_system_end:   int 	(> n_system_start)
	- start_time:     float (Julian Date)
	- n_time_points:  int	(number of time points to calculate)
	- time_step:      float (step between time points)
	- dps_mode:
	- radius_mode:
	- transit_crit: 'planetary' or 'stellar'
	- verbose:        bool	(display messages)

	# n_system_start & n_system_end refer to the (n-th system) in the table
	# include: n_system_start
	# doesn't include: n_system_end
	"""

	#execfile('transit_funcs.py')
	#execfile('planet_categorize.py')

	# setting parameters

	BJD=2456155.0                     # August 15th 2012, initial start time for the plot
	end_time = start_time + n_time_points*time_step
	t = arange(start_time, end_time, time_step) # step = 1/10000.0 (10k points per day)
	t = t - 2454900 # As in the table
	#t=arange(10000.0)/100+BJD
	#t=arange(1000000.0)/10000+BJD          #ends August 29 2012
	AU_to_solR = 1/0.0046491  # convert from AU to solar Radius 

	if verbose:
		print 'start_time: '+str(start_time)+' end_time: '+str(end_time)
		print 'length_of_time_vector: '+str(size(t))


	# Get information about the selected systems
	planet_systems, r_mode, dps_mode = planet_categorize(t, n_system_start, n_system_end, dps_mode, radius_mode, df_dir, verbose = verbose)
	if transit_crit == 'user_input':
		transit_crit_n = input('Please select criterion for determing planet transit: \n1)Planetary radius\n2)Stellar radius')
		transit_crits = ['planetary', 'stellar']
		transit_crit = transit_crits[transit_crit_n-1]


	# run through each system, find the angular separation
	sys_keys = planet_systems.keys() # keys, system indexes
	sys_transit_time = {}  # a new top-level dictionary, with system name as key words, as well
	for k in sys_keys:
		n_members = size(planet_systems[k])
		sys_transit_time[k] = {'n_planets':n_members}   
		# under each keywords, (each system), we have sub-dictionaries, with # of planets as key words
		# 	sys_transit_time = { sys_id0:  {'n_planets': 3,
		#					'2':{  (planet0, planet1): 
		#					           {'start_points':[], 'end_points':[] \
		#						    's_ang_sep':[], 'e_ang_sep':[],  \
		#						    'transit_period':[], 'non_transit_period':[]  \
		#						    'n_transits': <int>, \
		#					 	    'participants_periods':[]}, 	
		#					       (planet1, planet2):
		#						   { },...}, 
		#					'3':{}, ...} , 
		#			     sys_id1:  {}, 
		#			     sys_id2:  {}, ...}
		# For a system that have N planets, we need to find when 2, 3, ...,N planets are in conjunction
		for i in range(2, n_members+1):
			# in each dictioanry with i as keywords (# of planets), we have
			# 		yet another dictionary, with *participants* as keywords, 
			#		content is a dictionary with 'start_time', 'end_time' as keywords 
			transit_time_tmp, acc_n_conjunctions = find_transit_time(planet_systems[k], i, t, \
								 transit_crit, planet_systems[k][0]['Rad2'], \
								acc_n_conjunctions, verbose = verbose)
			sys_transit_time[k][str(i)] = transit_time_tmp
			if verbose:
				print '..................................................'
				print 'Current system: '+str(k)
				print 'Searching for conjuction of '+str(i)+' planets...'
				print 'Found conjuction: '+ str(transit_time_tmp.keys())
				print '..................................................'
			#if can't find any conjuction for current number of planets, no need to continue
			if not transit_time_tmp.keys():
				if verbose:
					print 'No conjuction found for '+str(i)+' planets...'
					print 'Stop searching for current system'
				break
		# after searching for planet conjunction, delete current system to free up space
		del planet_systems[k]
				

	if save_to_file:
		# write to file
		transit_time_file_name = 'transit_time_system_'+str(n_system_start) +'th_to_'+\
			str(n_system_end-1)+'th_time_'+str(start_time)+'_'+str(end_time)
		transit_time_save_to_file(df_dir+transit_time_file_name, sys_transit_time, \
					r_mode, dps_mode, transit_crit,\
					start_time, end_time, pickle_file = True)
	else:
		transit_time_file_name = ''
	
	return sys_transit_time, acc_n_conjunctions, transit_time_file_name, dps_mode, r_mode, transit_crit, start_time, end_time
