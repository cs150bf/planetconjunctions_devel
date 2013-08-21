from numpy import *
from scipy import *
from itertools import *
import pickle
import pylab


def transit_time_readin(filename, verbose = False):
	"""
	Return a dictionary: sys_transit_time
	under each keywords, (each system), we have sub-dictionaries, with # of planets as key words
	sys_transit_time = { sys_id0:  {'n_planets': 3,
					'2':{  (planet0, planet1): 				
					    		{'start_points':[], 'end_points':[] \
							 's_ang_sep':[], 'e_ang_sep':[],  \
							 'transit_period':[], 'non_transit_period':[]  \
							 'n_transits': <int>},	
					       (planet1, planet2):
						 	{ },...}, 
					'3':{}, ...} , 
			     sys_id1:  {}, 
			     sys_id2:  {}, ...}
	For a system that have N planets, we need to find when 2, 3, ...,N planets are in conjunction
	"""
	if verbose:
		print 'Reading file: '+filename+'.pickle'
	pkfile = open(filename+'.pickle', 'r')
	sys_transit_time = pickle.load(pkfile)
	return sys_transit_time

def transit_timeline_printout(filename, transit_timeline, date_format='jd', pickle_file=False):
    fns = []
    if pickle_file:
	pkfile = open(filename+'.pickle', 'w')
        fns.append(filename+'.pickle')
	pickle.dump(transit_timeline, pkfile)
	pkfile.close()
    datafile=open(filename+'.txt', 'w')
    fns.append(filename+'.txt')
    for timepoint in sorted(transit_timeline.keys()):
	datafile.write('============================================\n')
	if date_format == 'jd':
		datafile.write('Start time (JD): '+str(timepoint+2454900)+'\n')
	else:
		datafile.write('Start time (UTC): '+str(dates.num2date(dates.julian2num(timepoint+2454900)))+'\n')
	for sys_id in sorted(transit_timeline[timepoint].keys()):
		datafile.write('-----------------------------------\n')
		datafile.write('\tSystem '+str(sys_id)+' :\n')
		for participants in sorted(transit_timeline[timepoint][sys_id].keys()):
			tmp_dict = transit_timeline[timepoint][sys_id][participants]
			datafile.write('\t\tParticipants :'+str(participants)+'\n')
			if date_format == 'jd':
				datafile.write('\t\t\tStart_time (JD) :'+str(timepoint+2454900)+'\n')
				datafile.write('\t\t\tEnd_time (JD) :'+str(tmp_dict['end_time']+2454900)+'\n')
			else:
				datafile.write('\t\t\tStart_time (UTC):'+str(dates.num2date(dates.julian2num(timepoint+2454900)))+'\n')
				datafile.write('\t\t\tEnd_time (UTC):'+str(dates.num2date(dates.julian2num(tmp_dict['end_time']+2454900)))+'\n')
			datafile.write('\t\t\tTransit_period (hours):'+str(tmp_dict['transit_period']*24.0)+'\n')
			datafile.write('\t\t\tStart time separation (Solar Radius) :'+str(tmp_dict['s_ang_sep'])+'\n')
			datafile.write('\t\t\tEnd time separation (Solar Radius): '+str(tmp_dict['e_ang_sep'])+'\n')
			datafile.write('\t\t\tTotal size (Solar Radius) :'+str(tmp_dict['radius_sum'])+'\n')
    datafile.close()
    return fns
	

def transit_datafiles_timeline_sort(filenames, verbose=False):
    transit_timeline = {}
    for filename in filenames:
	if verbose:
		print 'Current file: ', filename
	sys_transit_time = transit_time_readin(filename, verbose=verbose)
        transit_timeline = transit_system_timeline_sort(transit_timeline, sys_transit_time)
    return transit_timeline
	
def transit_system_timeline_sort(transit_timeline, sys_transit_time):# run through all the systems
	for sys_id in sys_transit_time.keys():
		if verbose:
			print '\tCurrent system :', sys_id
		conjunction_flag = 0 # we should have this earlier
		for n_members in sys_transit_time[sys_id].keys():
			if n_members == 'n_planets':
				continue
			for participants in sorted(sys_transit_time[sys_id][n_members].keys()):
				n_transits = sys_transit_time[sys_id][n_members][participants]['n_transits']
				if n_transits <=0:
					continue
				if verbose:
					print '\tWe\'ve got some conjunction! Participating planets: ', participants
				start_times = sys_transit_time[sys_id][n_members][participants]['start_points']
				end_times = sys_transit_time[sys_id][n_members][participants]['end_points']
				s_ang_sep = sys_transit_time[sys_id][n_members][participants]['s_ang_sep']
				e_ang_sep = sys_transit_time[sys_id][n_members][participants]['e_ang_sep']
				radius_sum = sys_transit_time[sys_id][n_members][participants]['radius_sum']
				transit_period = sys_transit_time[sys_id][n_members][participants]['transit_period']
				non_transit_period = sys_transit_time[sys_id][n_members][participants]['non_transit_period']
				p_pers = sys_transit_time[sys_id][n_members][participants]['participants_periods']
				for i in range(0, len(start_times)):
					start_time = start_times[i]
					if verbose:
						print '\t\tCurrent start time: ', start_time	
					if len(end_times) <= i:
						end_time = -2454900
						e_ang_sep_tmp = -1
						t_period = -1
					else:
						end_time = end_times[i] 
						e_ang_sep_tmp = e_ang_sep[i] 
						t_period = transit_period[i]
					tmp_dict ={'end_time': end_time, 'transit_period':t_period, 'p_pers': p_pers, 's_ang_sep':s_ang_sep[i], 'e_ang_sep':e_ang_sep_tmp, 'radius_sum':radius_sum}	
					if verbose:
						print '\t\tcurrent dictionary: ', tmp_dict
					if transit_timeline.has_key(start_time):
						tr_list_at_t = transit_timeline[start_time]
						if tr_list_at_t.has_key(sys_id):
							tr_list_at_t[sys_id][participants]= tmp_dict				
						else:
							tr_list_at_t[sys_id]={participants:tmp_dict}	
					else:
						transit_timeline[start_time]={sys_id:{participants:tmp_dict}}
        return transit_timeline


def transit_times_stats(sys_transit_time, target_n_planets,  acc_time_per = 1.0, start_time = 2456069.0, \
			end_time = 2456169.0, verbose = False):
	"""
	Given a dictionary of transit times of multiple systems, accumulate for 
		acc_time_per from start_time to end_time, for transits of N(target_n_planets) planets
	Return a dictioanry of accumulated results (for every acc_time_per during the whole time span, how many
		transits of N planets occur, and among which planets do these transits happen

	transit_stats_dict = {  't_vec':t_vec, \
				'acc_vec':acc_vec, \
				'sys_acc_vec':sys_acc_vec, \
				'start_time': start_time, \
				'end_time': end_time, \
				'acc_time_per': acc_time_per, \
				'target_n_planets':target_n_planets}

	acc_vec:     a list of integers (# of planet alignment for N planets at each time period)
	sys_acc_vec: a list of dictionaries
	sys_dict:    a dictionary
			{sys_id0: [{'par_name': participants, \
				     'start_time':s_t, \
				     'end_time': e_t}, \
				    {}, \
				    {}], \
			sys_id1: [], \
			sys_id2: []}
	"""
	target_key = str(target_n_planets)

	t_vec = arange(start_time, end_time, acc_time_per)
	if t_vec[-1] < end_time:
		append(t_vec, end_time)
	acc_vec = zeros(size(t_vec)-1)
	sys_acc_vec = []
	for i in range(0, size(acc_vec)):
		sys_acc_vec.append({'-1':[]})
		if verbose:
			print 'sys_acc_vec[', str(i), '] :', str(sys_acc_vec[i])


	# run through all the systems
	# target_key is the number of planets to search conjunction of
	for sys_id in sys_transit_time.keys():
		if verbose:
			print 'Current system :', sys_id
		if sys_transit_time[sys_id].has_key(target_key):
			# run through all combinations of n_planets that has conjuctions
			for participants in sys_transit_time[sys_id][target_key].keys():
				if verbose:
					print 'Current planets :', participants
				s_t_tmp = sys_transit_time[sys_id][target_key][participants]['start_points']
				e_t_tmp = sys_transit_time[sys_id][target_key][participants]['end_points']
				t_search_start = 0
				# run through all the start points
				for i in range(0, size(s_t_tmp)):
					s_t = s_t_tmp[i]
					if i<size(e_t_tmp):
						e_t = e_t_tmp[i]
					else:
						e_t = -1
					# find which region does current start_time fall in
					for j in range(t_search_start, size(acc_vec)):
						if s_t < t_vec[j+1]:
							if verbose:
								print 'Current start time :', s_t
								print 'Current end time :', e_t
								print 'Current time accumulating period :', \
									t_vec[j], t_vec[j+1]
								print 'Current acc_vec[',str(j),'] :', acc_vec[j]
								print 'Current sys_dict[',str(j),'] size: ', size(sys_acc_vec[j])
							acc_vec[j] = acc_vec[j] + 1
							sys_dict = sys_acc_vec[j]
							if sys_dict.has_key(sys_id):
								participant_list = append(sys_dict[sys_id],\
											 ({'par_name': participants, \
											   'start_time':s_t, \
											   'end_time': e_t}))
							else:
								participant_list = [({'par_name': participants, \
										      'start_time':s_t, \
										      'end_time': e_t})]
							sys_dict.update({sys_id:participant_list})
							sys_acc_vec[j] = sys_dict
							t_search_start = j 
							# next start time, start searching from current region
							if verbose:
								print 'Updated participant list size :',\
									 size(participant_list)
								print 'Updated sys_dict size :', size(sys_dict.keys())
							break

	
	for i in range(0, size(sys_acc_vec)):
		sys_dict = sys_acc_vec[i]
		del sys_dict['-1']
		sys_acc_vec[i] = sys_dict

	transit_stats_dict = {  't_vec':t_vec, \
				'acc_vec':acc_vec, \
				'sys_acc_vec':sys_acc_vec, \
				'start_time': start_time, \
				'end_time': end_time, \
				'acc_time_per': acc_time_per, \
				'target_n_planets':target_n_planets}
	return transit_stats_dict



def transit_n_stats_save_to_file(filename, transit_stats_dict, dps_mode, r_mode, pickle_file = False):
	"""
	Given a dictioanry of accumulated results (for every acc_time_per during the whole time span, how many
		transits of N planets occur, and among which planets do these transits happen
	Write to file (always right to txt file, write to pickle file when pickle_file is True)

	transit_stats_dict = {  't_vec':t_vec, \
				'acc_vec':acc_vec, \
				'sys_acc_vec':sys_acc_vec, \
				'start_time': start_time, \
				'end_time': end_time, \
				'acc_time_per': acc_time_per, \
				'target_n_planets':target_n_planets}

	acc_vec:     a list of integers (# of planet alignment for N planets at each time period)
	sys_acc_vec: a list of dictionaries (details of alignments for N planets at each time period)
		sys_dict: a dictionary
			{sys_id0: [{'par_name': participants, \
				     'start_time':s_t, \
				     'end_time': e_t}, \
				    {}, \
				    {}], \
			sys_id1: [], \
			sys_id2: []}
	"""
	if pickle_file:
		pkfile = open(filename+'.pickle', 'w')
		pickle.dump(transit_stats_dict, pkfile)
		pkfile.close()

	datafile = open(filename+'.txt','w')
	
	t_vec = transit_stats_dict['t_vec']
	acc_vec = transit_stats_dict['acc_vec']
	sys_acc_vec = transit_stats_dict['sys_acc_vec']
	start_time = transit_stats_dict['start_time']
	end_time = transit_stats_dict['end_time']
	acc_time_per = transit_stats_dict['acc_time_per']
	target_n_planets = transit_stats_dict['target_n_planets']
	if size(target_n_planets) > 1:
		target_n_planets = unique(target_n_planets)

	datafile.write('Filename : '+filename+'\n')
	datafile.write('Search for planet alignment from time '+str(start_time)+ \
			' to '+str(end_time)+' for '+str(target_n_planets) + ' planets : \n')
	datafile.write('*********************************\n')	
	datafile.write('Planet radius : ' + r_mode +'\n')
	datafile.write('Distance from the planet to (earth-star) line of sight : '+ dps_mode + '\n')
	datafile.write('*********************************\n')
	for i in range(0, size(acc_vec)):
		datafile.write('\n------------------------------------\n')
		datafile.write('From time '+str(t_vec[i])+' to '+str(t_vec[i+1])+' :\n')
		datafile.write('\tNumber of transits of '+str(target_n_planets)+' planets :\n')
		datafile.write('\t\t'+str(acc_vec[i])+'\n')
		datafile.write('\tParticipants of these transits :\n')
		sys_dict = sys_acc_vec[i]
		for sys_id in sorted(sys_dict.keys()):
			datafile.write('\t\t----------------\n')
			datafile.write('\t\tSystem '+str(sys_id)+' :\n')
			for participants in sys_dict[sys_id]:
				datafile.write('\t\t\tParticipants :'+str(participants['par_name'])+'\n')
				datafile.write('\t\t\t\tStart time :'+str(participants['start_time'])+'\n')
				datafile.write('\t\t\t\tEnd time :'+str(participants['end_time'])+'\n')
			datafile.write('\t\t----------------\n')

	datafile.close()






def plot_transit_stats(target_n_planets = 2, acc_vec = [0], t_vec = [0, 1],\
			 acc_time_per = 1.0, pattern = '*', color = 'b', stack = False, bottom = [], verbose = False):
	"""
	"""
	if verbose:
		print 'Dimension of t_vec :', size(t_vec)
		print 'Dimension of acc_vec :', size(acc_vec)

	x_ind = []
	for i in range(0, size(acc_vec)):
		x_ind_tmp = 0.5*(t_vec[i+1]+t_vec[i])-t_vec[0]
		x_ind.append(x_ind_tmp)

	if pattern == 'bar':
		if stack:
			plot_obj = pylab.bar(t_vec[0:-1]-t_vec[0], acc_vec, width = acc_time_per*0.3,\
					 bottom = bottom, color = color, align = 'center')
		else:
			plot_obj = pylab.bar(t_vec[0:-1]-t_vec[0], acc_vec, width = acc_time_per*0.3, \
					 color = color, align = 'center')
	else:
		if stack:
			plot_obj = pylab.plot(x_ind, acc_vec+bottom, pattern, color = color)
			for i in range(0, size(acc_vec)):
				pylab.vlines(x = x_ind[i], ymin = bottom[i], ymax = acc_vec[i]+bottom[i], \
						lw = 2, color = color)
		else:
			plot_obj = pylab.plot(x_ind, acc_vec, pattern, color = color)
			for i in range(0, size(acc_vec)):
				pylab.vlines(x = x_ind[i], ymin = 0, ymax = acc_vec[i], lw = 2, color = color)

	plot_legend = 'Number of transits of '+str(target_n_planets)+' planets per '+str(acc_time_per)+' days'

	return plot_obj, plot_legend




def transit_stats_dict_update(combined_dict, new_dict, verbose = False):
	"""
	Join two dictionaries together
	"""
	if combined_dict.has_key('init'):
		if verbose:
			print 'New dictionary...'
		combined_dict.update(new_dict)
		combined_dict.update({'target_n_planets':[new_dict['target_n_planets']]})
		if verbose:
			print 'Current target_n_planets list ', combined_dict['target_n_planets']
		del combined_dict['init']
		return combined_dict
	
	acc_vec = new_dict['acc_vec']
	sys_acc_vec = new_dict['sys_acc_vec']
	target_n_planets = new_dict['target_n_planets']


	c_acc_vec = combined_dict['acc_vec']
	c_sys_acc_vec = combined_dict['sys_acc_vec']
	c_target_n_planets = combined_dict['target_n_planets']

	if verbose:
		print 'Current acc_vec :', str(c_acc_vec)
		print 'Current target_n_planets list :', c_target_n_planets

	c_acc_vec = c_acc_vec + acc_vec
	for i in range(0, size(c_sys_acc_vec)):
		c_sys_dict = c_sys_acc_vec[i]
		sys_dict = sys_acc_vec[i]
		for key in sys_dict.keys():
			if c_sys_dict.has_key(key):
				new_val = append(c_sys_dict[key], sys_dict[key])
				c_sys_dict.update({key:new_val})
			else:
				c_sys_dict.update({key:sys_dict[key]})
	c_target_n_planets.append(target_n_planets)

	if verbose:
		print 'Updated acc_vec :', str(c_acc_vec)
		print 'Updated target_n_planets list :', c_target_n_planets

	combined_dict.update({'acc_vec':c_acc_vec, 'sys_acc_vec':c_sys_acc_vec,  'target_n_planets':c_target_n_planets})
	return combined_dict
