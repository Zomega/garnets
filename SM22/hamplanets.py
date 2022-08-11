import numpy as np
import garnets as gar
import stellar_system

def specselect(in_spectyp):
    # Mass ranges from https://sites.uni.edu/morgans/astro/course/Notes/section2/spectralmasses.html
    # Age limits from 
    """Input a spectral type by letter (e.g. 'G'), as a string,
    output is an mass range array. """
    mass_ranges_by_spec = [
        [22.6, 32.7], #O
        [2.91, 17.8], #B
        [1.86, 2.48], #A
        [1.10, 1.59], #F
        [0.82, 1.05], #G
        [0.53, 0.76], #K
        [0.17, 0.49]  #M
    ]
    spectyp = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
    
    ### Add realistic main-sequence liftime limits here? Draw random age less than main sequence
    ### lifetime. Time on main sequence is M**-2.5 * 
    
    massrange = mass_ranges_by_spec[spectyp.index(str(in_spectyp))]
    return massrange

def givemeplanets(numsystems=3, spectyp='G'):
    """Makes solar systmes. (numsystems, spectyp):
    
    numsystems = the number of star systems with varying planets to make \
    spectyp = the stellar spectral type, must be input as e.g. 'A', 'G'. 
    
    Returns tuple with systems. First system callable as fubar[0].
    
    Ex.
    fubar = givemeplanets(3, 'G') \
    will make three solar systems around a G-class main sequence star.
    will output a tuple fubar. fubar[0] is first system, fubar[0].planets will display those planets"""
    
    massrange = specselect(spectyp)
    
    stellmas = np.round(np.random.uniform(massrange[0], massrange[1], numsystems), 3)
    mslifetime  = np.round((stellmas**-2.5) * 12, 5) #common formula for estimating MS lifetime relative to Sun, in Gyr
    stellage  = np.round(np.random.uniform(0.1, mslifetime), 5)  #in Gyr, draws random age from possible MS lifetime; 
                                                                 #arbitrary minimum is 100 Myr. 
    
    systems = []
    for i in np.arange(len(stellmas)):
        star = stellar_system.Star(mass_ratio=stellmas[i], age=stellage[i])
        systems.append(gar.generate_stellar_system(star))
    return systems



### Some examples. 
#three_Gclass = givemeplanets(3, 'G') --> three systems for G-class main sequence star
#multiple_classes = (givemeplanets(3, 'G'), givemeplanets(3, 'A')) --> three G-class and 3 A-class, in the same tuple

#The output tuple can be indexed from system[n].planets[i].property.  Note that python index start from 0.
#Example:
# three_Gclass[0].planets --> will print the basic properties of all planets in first system. 
# three_Gclass[1].planets[0] --> will print the planet properties for the first planet(index 0) in the second system (index 0).
# three_Gclass[0].planets[0]. *pressing TAB/autofill* --> show all parameters recorded for a planet

#Attributes for EACH PLANET:
#orbit
#axial_tilt
#mass
#dust_mass
#gas_mass
#moons
#gas_giant
#moon_a
#moon_e
#core_radius
#radius
#orbit_zone
#density
#orb_period
#day
#resonant_period
#esc_velocity
#surf_accel
#surf_grav
#rms_velocity
#molec_weight
#volatile_gas_inventory
#surf_pressure
#greenhouse_effect
#boil_po
#albedo
#exospheric_temp
#estimated_temp
#estimated_terr_temp
#surf_temp
#greenhs_rise
#high_temp
#low_temp
#max_temp
#min_temp
#hydrosphere
#cloud_cover
#ice_cover
#sun
#atmosphere
#type
#boil_point