from numpy import *
from scipy import *
from itertools import *
import pickle
import matplotlib.dates as dates




def find_radius_sum(planet_sys):
	"""	
	# input planet_sys is a list, with each item being a dictionary
	# 	with planet parameters as keywords (e.g. 'per', 'dist_p_to_s', etc)
	# return the sum of radius of all the planets in planet_sys
	"""
	radius_sum = 0.0
	for i in range(0, size(planet_sys)):
		radius_tmp = planet_sys[i]['radius']
		radius_sum = radius_sum + radius_tmp
	return radius_sum

def get_current_p_to_s(planet, t_current):
	"""
	Return the current angular separation of the given planet to its star
	"""
	p_to_s = planet['d']*sin(2*pi*(t_current-planet['t_0'])/planet['per'])
	return p_to_s


def find_current_max_separation(planet_sys, t_ind, t_current, n_participants, verbose = False):
	"""
	-planet_sys:		list
	-t_ind:			int
	-t_current:		float
	-n_participants:	int
	-verbose:		bool

	# given t_current (a single time point), 
	# find the max separation (AU) in given group of planets
	# return:
	# 	max_sep, planet_x, planet_y
	"""
	max_sep = 0
	planet_x = -1
	planet_y = -1 # initialize, to find when the max separationa occur
	iter_inds = combinations(range(0, n_participants), 2)  # separation (AU) between any 2 planets	
	for comb in iter_inds: # loop through any two planets in the given system
		#if verbose:
			#print 'Finding max separation at current time...'+str(t_ind)+', '+str(t_current)
			#print 'Current combination: ', str(comb)
		# get two planets
		x_dist_p_to_s = planet_sys[comb[0]]['dist_p_to_s_arr'][t_ind]
		y_dist_p_to_s = planet_sys[comb[1]]['dist_p_to_s_arr'][t_ind]
		#x_dist_p_to_s = get_current_p_to_s(planet_sys[comb[0]], t_current)
		#y_dist_p_to_s = get_current_p_to_s(planet_sys[comb[1]], t_current)
		# find their separation
		sep_tmp_t_current = abs(x_dist_p_to_s - y_dist_p_to_s)
		if sep_tmp_t_current > max_sep:
			max_sep = sep_tmp_t_current
			planet_x = comb[0]
			planet_y = comb[1]

	return max_sep, planet_x, planet_y
			



def find_conj_time(planet_sys, n_participants, t, conjunction_crit, stellar_R, acc_n_conjunctions=0, verbose = False):
	"""
	-planet_sys:		a list	 	(a list of planets)
	-n_participants:	int		(number of planets to search for conjuction)
	-t:			vector of floats(time vector)
	-conjunction_crit:		string, either 'planetary' or 'stellar', the criterion for finding conjunction
	-stellar_R:		float, stellar radius
	-verbose:		bool

	# input planet_sys is a list, each item in the list is another dictionary, 
	# with planet parameters as keywords (e.g. 'per', 'dist_p_to_s', etc)
	#
	# return a dictionary, with *participants* as keyword
	#	and the content is yet another dictionary, with
	#	'start time', 'end time', 's_ang_sep', 
	#	'e_ang_sep', 'conj_crit', 'number of conjunctions' as keywords
	# Example:
	# conj_times = {(planet0, planet1) : {'start_points':[], 'end_points':[],  \
	#					 's_ang_sep':[], 'e_ang_sep':[], \
	#					 'conjunction_period':[], 'non_conjunction_period':[], \
	#					 'conj_crit':<float> , 'n_conjs': <int>, \
	#					 'participants_periods':[]},  
	#		   (planet1, planet2) : {...},
	#		  }
	"""
	conj_times = {}
	n_planets = size(planet_sys) # planet_sys is a *list*
	iter_inds = combinations(range(0, n_planets), n_participants)

	# try every combinations of N planets in the given system
	for comb in iter_inds:  # comb is a tuple of keys
		if verbose:
			print 'Current combination: ', str(comb)

		ineffective_flag = False
		planet_group = [] # create a smaller *list*, basically a subset of planet_sys
		for j in range(0, n_participants): # get the planets given by *comb*
			planet_group.append(planet_sys[comb[j]])
			if planet_sys[comb[j]]['radius'] < 0:
				ineffective_flag = True
			if planet_sys[comb[j]]['d_to_Rstar'] < 0:
				ineffective_flag = True

		if ineffective_flag:
			if verbose:
				print 'Ineffective value found in current combination, continue....'
			continue


		# scan through time vector to find start & end points
		if conjunction_crit == 'planetary':
			conj_crit = find_radius_sum(planet_group) # radius_sum = radius_1 + radius_2 + radius_3 + ... + radius_n
		elif conjunction_crit == 'stellar':
			conj_crit = stellar_R
		else:
			print 'Invalid value for parameter conjunction_crit, set to default: stellar_R'
			conj_crit = stellar_R 

		started_flag = 0 # if this is true, we are currently in an on-going conjunction; when a conjunction start point found, change this to 1
		start_t_points = []
		end_t_points = []
		start_ang_separation = []
		end_ang_separation = []
		incomplete_flag = 0 # whether the conjunctions we found are all complete
		notes=[]

		for t_ind in range(0, size(t)): # time index
			t_current = t[t_ind]
			max_separation_current, planet_x, planet_y  = find_current_max_separation(planet_group,t_ind, t_current, n_participants, verbose = verbose)


			# if max separation (AU) is smaller than conj_crit
			# 	and t_current is not already in a conjunction zone
			#	(It's possible that we started our calculation right in the middle of a conjunction)
			if (not started_flag) and (max_separation_current < conj_crit): 
				if verbose:
					print 'A start point is found!'
					print 'Current start time: ', str(t_current)
					print ('Current max separation: ', str(max_separation_current), \
						', planet ', str(planet_x), ', planet ', str(planet_y))
					print 'Conjunction Criterion: ', str(conj_crit)
				started_flag = 1
				start_t_points.append(t_current) # add start point (time stamp)
				start_ang_separation.append(max_separation_current) # record current separation (AU))
				if t_ind == 0: # right at the beginning of our observing window
					if verbose:
						print 'This start point is right at the beginning of our observing window...'
					incomplete_flag = incomplete_flag+1
					notes.append('First conjunction started before the observation started')

			# if we are stepping out of the conjunction zone
			elif started_flag and not(max_separation_current < conj_crit): 
				if verbose:
					print 'An end point is found!'
					print 'Current end time: ', str(t_current)
					print ('Current max separation: ', str(max_separation_current), \
						', planet ', str(planet_x), ', planet ', str(planet_y))
					print 'Conjunction Criterion: ', str(conj_crit)
				started_flag = 0 # out of conjunction zone
				end_t_points.append(t_current) # add end point(time stamp)
				end_ang_separation.append(max_separation_current) # record current separation (AU))
			# if we are finishing up before a conjunction ends
			elif started_flag and t_ind==size(t)-1: # observation ended while in the middle of a conjunction
				if verbose:
					print 'Our observation is finishing, but a conjunction is still on-going...'
					print 'Current end time: ', str(t_current)
					print ('Current max separation: ', str(max_separation_current), \
						', planet ', str(planet_x), ', planet ', str(planet_y))
					print 'Conjunction Criterion: ', str(conj_crit) 
				incomplete_flag=incomplete_flag+2
				started_flag = 0
				end_t_points.append(t_current)
				end_ang_separation.append(max_separation_current)
				notes.append('Last conjunction is still on-going when the observation ended')
		if verbose:		
			print 'Number of start points: '+str(size(start_t_points))
			print 'Number of end points: '+str(size(end_t_points))

		conjunction_period = []
		non_conjunction_period = [0.0]
		if size(start_t_points) != size(end_t_points):
			# if this happens, there must be something wrong...
			if verbose:
				print 'Start points & End points don''t agree! Setting number of conjunctions to -1'
			n_conjs = -1
		else:
			n_conjs = size(end_t_points)
			mid_t_points = zeros(n_conjs)
			for i in range(0, n_conjs):
				mid_t_points[i] = (end_t_points[i] + start_t_points[i])*0.5
			for i in range(0, n_conjs):
				conjunction_period.append(end_t_points[i]- start_t_points[i])
			for i in range(1, n_conjs):
				non_conjunction_period.append(start_t_points[i] - end_t_points[i-1])
		
		participants_local_ind = str(comb) # index of participants in planet_sys
		participants = [] # a list of 'number's
		participants_periods = []
		participants_radii = []
		participants_teqs = []
		for participant_ind in comb:
			participants.append('{0:04.2f}'.format(float(planet_sys[participant_ind]['number'])))
			participants_teqs.append(planet_sys[participant_ind]['Teq'])
			participants_periods.append(planet_sys[participant_ind]['per'])
			participants_radii.append(planet_sys[participant_ind]['radius'])

		if verbose:
			print 'participants: ', participants

		participants = str(participants) # a list can't be a key of a dicionary

		
		if n_conjs:  # if n_conjs != 0,  this doesn't exclude the n_conjs == -1 case
			conj_times[participants] = {'start_points': start_t_points,\
							'end_points':end_t_points, \
							'mid_points': mid_t_points, \
							's_ang_sep': start_ang_separation, \
							'e_ang_sep': end_ang_separation, \
							'conj_crit':  conj_crit, \
							'conjunction_period': conjunction_period, \
							'non_conjunction_period': non_conjunction_period, \
							'n_conjs':n_conjs, \
							'participants_periods':participants_periods, \
							'participants_radii':participants_radii, \
							'participants_teqs':participants_teqs, \
							'incomplete_flag':incomplete_flag, \
							'notes': notes}

		if n_conjs>=0:
			acc_n_conjunctions = acc_n_conjunctions + n_conjs

	return conj_times, acc_n_conjunctions # return a dictionary
	# conj_times = {(planet0, planet1) : {'start_points':[], 'end_points':[],  \
	#					 's_ang_sep':[], 'e_ang_sep':[],  \
	#					 'conjunction_period':[], 'non_conjunction_period':[]  \
	#					 'n_conjs': <int>, \
	#					 'participants_periods':[]}, 
	#		   (planet1, planet2) : {...},
	#		  }





def planet_sys_save_to_file(filename, planet_system, global_s_time, global_e_time, pickle_file = False):
	""" 	
	-filename:  	string		(doesn't include format)
	-planet_system: dictionary
	-global_s_time: float
	-global_e_time: float
	-verbose:	bool
	
	# always write to txt file
	"""
	fns = []
	if pickle_file:
		#print pickle_file
		pkfile = open(filename+'.pickle', 'w')
		fns.append(filename+'.pickle')
		pickle.dump(planet_system, pkfile)
		pkfile.close()

	datafile = open(filename+'.txt','w')
	fns.append(filename+'.txt')
	datafile.write('Search for planet conjuction from time '+str(global_s_time)+' to '+str(global_e_time)+': \n')
	datafile.write('*********************************\n')
	datafile.write('Planet radius : '+planet_system['radius_mode']+'\n')
	del planet_system['radius_mode']
	datafile.write('Distance from the planet to (earth-star) line of sight : '\
			+planet_system['dist_planet_to_(earth-star)_mode']+'\n')
	del planet_system['dist_planet_to_(earth-star)_mode']
	datafile.write('*********************************\n')
	for sys_n in sorted(planet_system.keys()):
		datafile.write('System '+str(sys_n)+':\n')
		datafile.write(str(size(planet_system[sys_n]))+' planets: \n')
		for planet in planet_system[sys_n]:
			datafile.write('\t----------------\n')
			if planet.has_key('number'):
				datafile.write('\t'+str(planet['number'])+': \n')
			for key in planet.keys():
				datafile.write('\t\t'+str(key)+': '+str(planet[key])+'\n')
			datafile.write('\t----------------\n')
		datafile.write('\n------------------------------------\n')
	datafile.close()
	return fns




def conj_time_save_to_file(filename, sys_conj_time, r_mode, dps_mode, conjunction_crit, \
				global_s_time, global_e_time, date_format='jd', pickle_file = False, to_append = False):
	""" 	
	-filename:  		string		(doesn't include format)
	-sys_conj_time: 	dictionary
	-r_mode: 		string
	-dps_mode:		string
	-global_s_time: 	float
	-global_e_time: 	float
	-verbose:		bool
	
	# always write to txt file
	"""
	fns = []
	if pickle_file:
		if to_append:
			pkfile = open(filename+'.pickle', 'a+b')
		else:
			pkfile = open(filename+'.pickle', 'w')
		fns.append(filename+'.pickle')
		pickle.dump(sys_conj_time, pkfile)
		pkfile.close()
	if to_append:
		datafile = open(filename+'.txt','a+b')
	else:
		datafile = open(filename+'.txt','w')
	fns.append(filename+'.txt')
	if date_format == 'jd':
		global_s_time_str = str(global_s_time)
		global_e_time_str = str(global_e_time)
	else:
		global_s_time_str = str(dates.num2date(dates.julian2num(global_s_time)))
		global_e_time_str = str(dates.num2date(dates.julian2num(global_e_time)))
	datafile.write('Search for planet conjuction from time '+global_s_time_str+' to '+global_e_time_str+': \n')
	datafile.write('*********************************\n')
	datafile.write('Planet radius : ' + r_mode +'\n')
	datafile.write('Distance from the planet to (earth-star) line of sight : '+ dps_mode + '\n')
	datafile.write('*********************************\n')
	datafile.write('Criterion for conjunction (distance <= ?): '+conjunction_crit+'\n')
	datafile.write('*********************************\n')
	for sys_n in sorted(sys_conj_time.keys()):
	        # datafile.write('System '+str(sys_n)+' (number of planets: '+ \
		#		str(sys_conj_time[sys_n]['n_planets'])+'): \n')
		sys_str = 'System '+str(sys_n)+' (number of planets: '+ \
					str(sys_conj_time[sys_n]['n_planets'])+'): \n'
		sys_str_print = 0
		for n_members in sorted(sys_conj_time[sys_n].keys()):
			if n_members == 'n_planets':
				continue
			# datafile.write('\t----------------\n')
			# datafile.write('\tSearching alignment of '+str(n_members)+' planets: \n')
			search_str = '\t----------------\n\tSearching alignment of '+str(n_members)+' planets: \n'
			search_str_print = 0
			for participants in sorted(sys_conj_time[sys_n][n_members].keys()):
				n_conjs = sys_conj_time[sys_n][n_members][participants]['n_conjs']
				if n_conjs <= 0:
					continue
				else:
					if sys_str_print == 0:
						datafile.write(sys_str)
						sys_str_print = 1
					if search_str_print == 0:
						datafile.write(search_str)
						search_str_print = 1
				datafile.write('\t\t----------------\n')
				datafile.write('\t\tParticipants: '+ str(participants)+': \n')
				start_times = sys_conj_time[sys_n][n_members][participants]['start_points']
				end_times = sys_conj_time[sys_n][n_members][participants]['end_points']
				mid_times = sys_conj_time[sys_n][n_members][participants]['mid_points']
				s_ang_sep = sys_conj_time[sys_n][n_members][participants]['s_ang_sep']
				e_ang_sep = sys_conj_time[sys_n][n_members][participants]['e_ang_sep']
				conj_crit = sys_conj_time[sys_n][n_members][participants]['conj_crit']
				conjunction_period = sys_conj_time[sys_n][n_members][participants]['conjunction_period']
				non_conjunction_period = sys_conj_time[sys_n][n_members][participants]['non_conjunction_period']
				p_pers = sys_conj_time[sys_n][n_members][participants]['participants_periods']
				p_radii = sys_conj_time[sys_n][n_members][participants]['participants_radii']
				p_teqs = sys_conj_time[sys_n][n_members][participants]['participants_teqs']
				incomplete_flag = sys_conj_time[sys_n][n_members][participants]['incomplete_flag']
				notes = sys_conj_time[sys_n][n_members][participants]['notes']

				datafile.write('\t\tConjunctions start at: \n')
				if date_format == 'jd':
					datafile.write('\t\t\t'+str([x+2454900 for x in start_times])+'\n')
				else:
					for x in start_times:
						datafile.write('\t\t\t')
						datafile.write(str(dates.num2date(dates.julian2num(x+2454900)))+'\n')
				datafile.write('\t\tConjunctions end at: \n')
				if date_format =='jd':
					datafile.write('\t\t\t'+str([x+2454900 for x in end_times])+'\n')
				else:	
					for x in end_times:
						if x < 0:
							x_str = '0'
						else:
							x_str =str(dates.num2date(dates.julian2num(x+2454900)))
						datafile.write('\t\t\t'+x_str+'\n')
				datafile.write('\t\t>>> Mid time: \n')
				if date_format == 'jd':
					datafile.write('\t\t\t'+str([x+2454900 for x in mid_times])+'\n')
				else:
					for x in mid_times:
						datafile.write('\t\t\t')
						datafile.write(str(dates.num2date(dates.julian2num(x+2454900)))+'\n')
				datafile.write('\t\t  Conjunction Criterion (unit: Solar Radius): \n')
				datafile.write('\t\t\t'+str(conj_crit)+'\n')
				datafile.write('\t\t  Number of Conjunctions: \n')
				datafile.write('\t\t\t'+str(n_conjs)+'\n')
				datafile.write('\t\t  Maximum separation among planets when conjunction starts (unit: Solar Radius): \n')
				datafile.write('\t\t\t'+str(s_ang_sep)+'\n')
				datafile.write('\t\t  Maximum separation among planets when conjunction ended (unit: Solar Radius): \n')
				datafile.write('\t\t\t'+str(e_ang_sep)+'\n')
				datafile.write('\t\t  Conjunction durations (hours): \n')
				datafile.write('\t\t\t'+str([p*24.0 for p in conjunction_period])+'\n')
				datafile.write('\t\t  Time period between conjunctions (hours): \n')
				datafile.write('\t\t\t'+str([p*24.0 for p in non_conjunction_period])+'\n')
				datafile.write('\t\t  Period of participants (days): \n')
				datafile.write('\t\t\t'+str(p_pers)+'\n')
				datafile.write('\t\t  Radii of participants (unit: Solar Radius):\n')
				datafile.write('\t\t\t'+str(p_radii)+'\n')
				datafile.write('\t\t  Equilibrium temperature of participants (unit: Solar Radius):\n')
				datafile.write('\t\t\t'+str(p_teqs)+'\n')
				if incomplete_flag:
					datafile.write('\t\tNote: there are incomplete conjunctions recorded!\n')
				for note_item in notes:
					datafile.write('\t\t\t'+note_item+'\n')
				datafile.write('\t\t----------------\n')
			if search_str_print:
				datafile.write('\t----------------\n')
		if sys_str_print:
			datafile.write('\n------------------------------------\n')
	datafile.close()
	return fns
	
