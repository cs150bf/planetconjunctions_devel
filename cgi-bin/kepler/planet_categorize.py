from scipy.io.idl import readsav
from numpy import *
import pickle

#execfil('planet_d_r_comparison.py')


# IDL code used to transfer data from txt format into idl save file
'''
pro data_idl_to_python

readcol, 'data.txt', name, KIC, Kp, t_0, t_0_unc, P, P_unc, Rp, a, T_eq, Dur, Depth, a_to_Rstar, a_to_Rstar_unc, r_to_Rstar, r_to_Rstar_unc, b, b_unc, SNR, chi, T_eff, log_g, Rad2, f_T_eff, /silent

save, name, KIC, Kp, t_0, t_0_unc, P, P_unc, Rp, a, T_eq, Dur, Depth, a_to_Rstar, a_to_Rstar_unc, r_to_Rstar, r_to_Rstar_unc, b, b_unc, SNR, chi, T_eff, log_g, Rad2, f_T_eff, filename = 'data.sav'
end
'''
# Noteworthy parameters:
#
# [a]:
# Semi-major axis of orbit (3)
# unit: AU, format: F6.3
# [p]:
# Average interval between conjunctions (1)
# unit: d,  format: F12.7
# [d_to_Rstar]:
# Ratio of planet-star separation to stellar radius
# unit: ---, format: F11.6
# [r_to_Rstar]:
# Ratio of planet radius to stellar radius
# unit: ---, format: F8.5
# [Rad]:
# Planet radius in earth radii = 6378 km
# unit: ---, format: F6.2
# [Rad2]:
# Stellar radius
# unit: solRad, format: F6.2
# [t_0]:
# time array





def planet_categorize(t_vec, n_system_start = 0, n_system_end = 5, \
			dist_p_to_s_mode = 'user_input', radius_mode = 'user_input', \
			df_dir='./', save_to_file = False, verbose = False):
	"""
	-t_vec:			vector/list		(time vector)
	-n_system_start: int 	(> 0)			
	-n_system_end:   int 	(> n_system_start)	
	-verbose:		bool

	# n_system_start & n_system_end refer to the (n-th system) in the table
	# include: n_system_start
	# doesn't include: n_system_end

	# Assuming the entries in given datafile are ordered according to their system number
	# Return a dictionary containing related information of selected planet systems
	#	[Keyword: Content]
	#
	# 	-System number(e.g. 15): [] (list)
	#	    items in the list: planets  (stored as dictionaries)
	#		-'number': (e.g. 15.01)
	#		-'a':
	#		-'per':
	#		-'Rad2':
	#		-'Rad':
	#		-'d_to_Rstar':
	#		-'r_to_Rstar':
	#		-'dist_p_to_s_arr':
	#		-'radius':
	"""
	#execfile('conjunction_funcs.py')


	if verbose:
		print 'start_time: '+str(t_vec[0])+' end_time: '+str(t_vec[-1])
		print 'length_of_time_vector: '+str(size(t_vec))


	
	AU_to_solR = 1/0.0046491  # convert from AU to solar Radius 
	earth_radii = 6378  # km
	km_to_solR = 1.0/(6.955*1e5)

	data = readsav('data_aug15.sav', verbose = verbose)
	planet_ind = data.name
	planet_a = data.a
	planet_per = data.p
	d_to_Rstar = data.a_to_Rstar
	r_to_Rstar = data.r_to_Rstar
	planet_rad = data.Rp
	stellar_rad2 = data.Rad2
	t_0 = data.t_0
	teq = data.T_eq
	planet_systems = {}

	planet_d1, planet_d2, planet_r1, planet_r2 = planet_d_r_comparison(save_to_file=False)

	if dist_p_to_s_mode == 'user_input':
		dist_p_to_s_mode = raw_input('Please select which planet-separation to use in computation (1 or 2):\n1) a: Semi-major axis of the orbit \n2) (d/R*)xRad2: (ratio of planet-star separation to stellar radius)*(stellar radius\n')
	if radius_mode == 'user_input':
		radius_mode = raw_input('Please select which planet radius to use in computation (1 or 2):\n1) Rad: Planet radius \n2) (r/R*)xRad2: (ratio of planet radius to stellar radius)*(stellar radius)\n')

	if radius_mode == '1' or radius_mode == 'default':
		r_mode = '1) Rad: Planet radius'
		r_arr = planet_r1
	elif radius_mode == '2':
		r_mode = '2) (r/R*)xRad2: (ratio of planet radius to stellar radius)*(stellar radius)'
		r_arr = planet_r2
	else:
		if verbose:
			print 'Invalid input, using default option, 1...'
		r_mode = '1) Rad: Planet radius' # default		
		r_arr = planet_r1

	if dist_p_to_s_mode == '1' or dist_p_to_s_mode == 'default':
		dps_mode = '1) a: Semi-major axis of the orbit'
		d_arr = planet_d1
	elif dist_p_to_s_mode == '2':
		dps_mode = '2) (d/R*)xRad2: (ratio of planet-star separation to stellar radius)*(stellar radius)'
		d_arr = planet_d2
	else:
		if verbose:
			print 'Invalid input, using default option, 1...'
		dps_mode = '1) a: Semi-major axis of the orbit' # default
		d_arr = planet_d1

	planet_d1, planet_d2, planet_r1, planet_r2 = 0, 0, 0, 0 # free up some space

	if verbose:
		print 'Current dist_p_to_s_mode :', dps_mode
		print 'Current radius_mode :', r_mode


	# categorized selected planets into systems
	# 	planet_systems = { sys_id0:[planet0, planet1, planet2, ...], sys_id1:[], sys_id2:[], ...}
	#	top-level dictionary, key-words are system indexes, contents are lists of planets
	sys_count = 0
	for i in range(0, size(planet_ind)):

		# how many systems we have by now 
		# (including systems in selectd range (n_system_start -> n_system_end), 
		# and systems before n_system_start)
		sys_count = size(planet_systems.keys()) 

		ind = int(floor(planet_ind[i]))  # this index will decide which system this planet is in
		if planet_systems.has_key(ind): # current planet belongs to an recorded system
			sys_planets = planet_systems[ind] # get a list of planets in current system
		elif (sys_count < n_system_end): # current planet  doesn't belongs to any recorded system
			sys_planets = []  # empty list, will add a new system
			sys_count = sys_count + 1
		else:
			break

		if (sys_count >= n_system_start):
			# dist_p_to_s_arr: this is an array (time-depend)
			# representing the distance from the planet to the (earth-star) line of sight
			if d_to_Rstar[i] <> -99.0:
				sin_p_angs = sin(2*pi*(t_vec-t_0[i])/planet_per[i])
				dist_p_to_s_arr_tmp = d_arr[i]*sin_p_angs		
			else:
				if verbose:
					print 'Negative distance, setting dist_p_to_s_arr_tmp to [-99]...'
				dist_p_to_s_arr_tmp = [-99]
				sin_p_angs=[0]

			radius_tmp = r_arr[i]

			# A node: a planet with information that we need
			planet_tmp = {'number':planet_ind[i], 'a': planet_a[i], \
					'per': planet_per[i], 'r_to_Rstar': r_to_Rstar[i], \
					'd_to_Rstar': d_to_Rstar[i], 'd':d_arr[i], \
					'Rad2': stellar_rad2[i], 'Rad': planet_rad[i], \
					'radius':radius_tmp, 't_0':t_0[i], 'Teq':teq[i], \
					'dist_p_to_s_arr': dist_p_to_s_arr_tmp, 'planet_ang_position':sin_p_angs}
		else:
			planet_tmp = {}

		# update dictionary
		sys_planets.append(planet_tmp)
		planet_systems[ind] = sys_planets

		if verbose:
			print 'Number of systems so far: '+str(sys_count)
			if not planet_tmp:
				print 'Skipped current planet'
			else:
				print 'Current planet: '+str(planet_tmp['number'])


	if size(planet_systems.keys()) < n_system_start:
		if verbose:
			print 'No system found in range ', str(n_system_start), 'th to ', str(n_system_end), 'th...'
			print 'Returning (empty dictionary)...'
		return {}, r_mode, dps_mode

	# trim the unrecorded systems before n_system_start
	sorted_sys_keys = sorted(planet_systems.keys())
	for i in range(0, n_system_start):
		k = sorted_sys_keys[i]
		del planet_systems[k]
	for i in range(n_system_end+1, size(sorted_sys_keys)):
		k = sorted_sys_keys[i]
		del planet_systems[k]
	sorted_sys_keys = sorted(planet_systems.keys())
	if verbose:
		print 'start_system: '+str(n_system_start)+', sys_num: '+str(sorted_sys_keys[0])
		print 'end_system: '+str(n_system_end-1)+', sys_num: '+str(sorted_sys_keys[-1])
	

	planet_systems.update({'radius_mode': r_mode, 'dist_planet_to_(earth-star)_mode': dps_mode})
	if save_to_file:
		# save to file after dealing with the data
		planet_sys_filename = df_dir+'planet_systems_'+str(n_system_start) +'th_to_'+\
			str(n_system_end-1)+'th_time_'+str(t_vec[0])+'_'+str(t_vec[-1])
		planet_sys_save_to_file(planet_sys_filename, planet_systems, t_vec[0], t_vec[-1], pickle_file = False)

	for k in planet_systems.keys():
		# if there's only one planet in the system, no need to store the array
		if isinstance(k, int) and size(planet_systems[k]) == 1:
			del planet_systems[k][0]['dist_p_to_s_arr'] # free up some space
	
	return planet_systems, r_mode, dps_mode
