from scipy.io.idl import readsav
from numpy import *
from scipy import *
from itertools import *
import pickle
import pylab


def planet_d_r_comparison(save_to_file=False):
	"""
	"""
	AU_to_solR = 1/0.0046491  # convert from AU to solar Radius 
	earth_radii = 6378  # km
	km_to_solR = 1.0/(6.955*1e5)

	data = readsav('data_aug15.sav', verbose =False)
	planet_ind = data.name
	planet_a = data.a
	d_to_Rstar = data.a_to_Rstar
	r_to_Rstar = data.r_to_Rstar
	planet_rad = data.Rp
	stellar_rad2 = data.Rad2
	dist_a = zeros(size(planet_ind))
	dist_dtoRxR = zeros(size(planet_ind))
	r_rad = zeros(size(planet_ind))
	r_rtoRxR = zeros(size(planet_ind))

	for i in range(0, size(planet_ind)):
		dist_a[i] = planet_a[i]*AU_to_solR
		dist_dtoRxR[i] = d_to_Rstar[i]*stellar_rad2[i]
		r_rad[i] = planet_rad[i]*earth_radii*km_to_solR
		r_rtoRxR[i] = r_to_Rstar[i]*stellar_rad2[i]

	if save_to_file:
		datafile = open('data_planets_d_r.txt', 'w')
		datafile.write('Planet information :\n')
		datafile.write('First Column: Kepler Object of Interest Number\n')
		datafile.write('Second Column: Semi-major axis of orbit (SolR)\n')
		datafile.write('Third Column: Ratio of planet-star separation to stellar radius TIMES stellar radius (SolR)\n')
		datafile.write('Fourth Column: Planetary radius (SolR)\n')
		datafile.write('Fifth Column: Ratio of planet radius to stellar radius TIMES stellar radius (SolR)\n')

		for i in range(0, size(planet_ind)):
			datafile.write('{0:<7.2f}'.format(float(planet_ind[i]))+'\t\t\t'+'{0:<15.8f}'.format(dist_a[i])+'\t\t\t'+'{0:<15.8f}'.format(dist_dtoRxR[i]))
			datafile.write('\t\t\t'+'{0:<15.8f}'.format(r_rad[i])+'\t\t\t'+'{0:<15.8f}'.format(r_rtoRxR[i])+'\n')

		datafile.close()
		
		datafile = open('data_planets_d_r.pickle','w')
		pickle.dump([dist_a, dist_dtoRxR, r_rad, r_rtoRxR], datafile)
		datafile.close()

	return dist_a, dist_dtoRxR, r_rad, r_rtoRxR
