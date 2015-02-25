import logging
logging.getLogger().setLevel(logging.INFO)

import random

from math import sqrt, exp, pi

###
# CONSTANTS
###

DUST_DENSITY_COEFF = 0.002
ECCENTRICITY_COEFF = 0.077

PROTOPLANET_MASS = 10.0**-15 # Units of solar masses. For scale, pluto clocks in at about 10^-8.
ALPHA = 5.0
B = 1.2 * 10**-5
N = 3.0
K = 50 #gas/dust ratio

SUN_MASS_IN_EARTH_MASSES = 332775.64

SUN_MASS_IN_MOON_MASSES = 27069000

SUN_MASS_IN_JUPITER_MASSES = 1047.2

DISK_ECCENTRICITY = 0.2

class Star:
	def __init__(self, mass_ratio, age):
		self.mass_ratio = mass_ratio
		self.age = age

	@property
	# Approximates the luminosity of the star.
	# TODO: express only as ratio?
	# Source: http://en.wikipedia.org/wiki/Mass%E2%80%93luminosity_relation
	def luminosity_ratio(self):
		if (self.mass_ratio < .43):
			return .23 * ( self.mass_ratio ** 2.3 )
		if (self.mass_ratio < 2):
			return ( self.mass_ratio ** 4 )
		# Main Sequence Stars
		if (self.mass_ratio < 20):
			return 1.5 * ( self.mass_ratio ** 3.5 )
		# For HUGE stars...
		return 3200 * self.mass_ratio

	@property
	# Source: StarGen, TODO Verify against current data.
	def stellar_dust_limit(self):
		return 200.0 * ( self.mass_ratio ** 0.3333 )

	@property
	# Source: StarGen, TODO Name? Value?
	def r_ecosphere(self):
		return sqrt(self.luminosity_ratio)

	@property
	# Source: StarGen, TODO Name? Value?
	def life(self):
		return 10**10 * (self.mass_ratio / self.luminosity_ratio);

class SolarSystem:
	def __init__( self, star, planets ):
		self.star = star
		self.planets = planets
		

def random_star(): # TODO: Add seed?
	# Source: http://exoplanets.co/exoplanet-correlations/host-star-mass-distribution.html
	# Source: http://en.wikipedia.org/wiki/Main_sequence#mediaviewer/File:HRDiagram.png
	# TODO: Code up generation.
	age = random.randrange(1*10**9, 6*10**9)
	mass = 1
	
	

def generate_stellar_system( star, do_gases = True, do_moons = True ):
	protoplanets = dist_planetary_masses( star, 0.0, star.stellar_dust_limit, do_moons)
	for p in protoplanets:
		print p
	flag_char = None # TODO: Remove / replace
	system = generate_planets( star, flag_char, do_gases, do_moons)
	return system

# Create protoplanets.

class CircumstellarDustLane:
	def __init__( self, inner_edge, outer_edge, dust_present, gas_present ):
		self.inner = inner_edge
		self.outer = outer_edge
		self.dust_present = dust_present # TODO: Switch to density.
		self.gas_present = gas_present # TODO: Switch to density
	def __repr__(self):
		return "\tINNER: " + str( self.inner ) + ", OUTER: " + str( self.outer ) + " D:" + str( self.dust_present ) + "\n"
	
	

class CircumstellarDisk: # TODO: Everything. Dust Lanes...
	def __init__( self, star ):
		self.star = star
		self.planet_inner_bound = 0.3 * ( star.mass_ratio ** 0.333 )
		self.planet_outer_bound = 50  * ( star.mass_ratio ** 0.333 )
		
		self.lanes = [CircumstellarDustLane(0, star.stellar_dust_limit, True, True)]

	def dust_density(self, a):
		return DUST_DENSITY_COEFF * sqrt( self.star.mass_ratio ) * exp( -ALPHA * ( a ** (1.0 / N) ) ) # TODO: This last term is a hack to get things working. It needs to be removed.

	@property
	def dust_left(self):
		# Check if we have any lanes on file with dust left!
		for lane in self.lanes:
			if lane.dust_present:
				return True
		return False
		
	def dust_available(self, inner, outer):
		for lane in self.lanes:
			# See if the lanes overlap.
			if (lane.inner <= inner and lane.outer > inner) or (lane.outer >= outer and lane.inner < outer):
				if lane.dust_present:
					return True
		return False

	def collect_dust(self, planetoid):
		new_dust_mass = 0
		new_gas_mass = 0
		for lane in self.lanes:
		
			# If the lane doesn't overlap, then we should just continue.
			if (lane.outer <= planetoid.inner_effect_limit) or (lane.inner >= planetoid.outer_effect_limit):
				continue
				
			# Now we need to figure out the density of gas and dust in the lane.
			if not lane.dust_present: # TODO: Refactor these quantities to be less planetoid specific.
				dust_density = 0.0
				gas_density = 0.0
			else:
				dust_density = self.dust_density(planetoid.a)
				if planetoid.mass < planetoid.critical_mass or ( not lane.gas_present ):
					gas_density = 0.0
				else:
					gas_density =  ( K - 1.0 ) * dust_density / (1.0 + sqrt( planetoid.critical_mass / planetoid.mass ) * (K - 1.0)) # TODO: This is DEEP Magic. Figure it out somehow.
					
				# Compute the width of the overlap between the region of effect and the lane.
				bandwidth = planetoid.outer_effect_limit - planetoid.inner_effect_limit
				
				width = min( lane.outer, planetoid.outer_effect_limit ) - max( lane.inner, planetoid.inner_effect_limit)
			
				temp1 = planetoid.outer_effect_limit - lane.outer;
				if (temp1 < 0.0):
					temp1 = 0.0
			
				temp2 = lane.inner - planetoid.inner_effect_limit;
				if (temp2 < 0.0):
					temp2 = 0.0
					
				temp = 4.0 * pi * ( planetoid.a ** 2.0 ) * planetoid.reduced_mass * (1.0 - planetoid.e * (temp1 - temp2) / bandwidth)
				volume = temp * width

				new_dust_mass += volume * dust_density
				new_gas_mass  += volume * gas_density		
		return new_dust_mass, new_gas_mass
			
	def update_dust_lanes(self, planetoid):
		# TODO: Refactor gas. This seems weird.
		if planetoid.mass > planetoid.critical_mass:
			gas = False
		else:
			gas = True
			
		new_lanes = []
		while len(self.lanes) > 0:
			lane = self.lanes.pop()
			
			# If the lane has neither dust nor gas, prune it.
			if not (lane.dust_present or lane.gas_present):
				continue
				
			# Now we see if the lane was overlapped at any point...
			if lane.outer <= planetoid.inner_effect_limit or lane.inner >= planetoid.outer_effect_limit:
				# There's no overlap, so the lane isn't affected.
				new_lanes.append(lane)
				continue
			
			if lane.inner < planetoid.inner_effect_limit:
				# Make an lane for the inside of the old lane
				new_lanes.append( CircumstellarDustLane( lane.inner, planetoid.inner_effect_limit, lane.dust_present, lane.gas_present ) )
			if lane.outer > planetoid.outer_effect_limit:
				print "OUTER"
				# Make an lane for the outside of the old lane
				new_lanes.append( CircumstellarDustLane( lane.outer, planetoid.outer_effect_limit, lane.dust_present, lane.gas_present ) )
			# Make a lane for the overlapped portion.
			new_lanes.append( CircumstellarDustLane( max( lane.inner, planetoid.inner_effect_limit ), min( lane.outer, planetoid.outer_effect_limit ), False, gas and lane.gas_present ) )
		self.lanes = new_lanes
		
	def accrete_dust(self, planetoid):
		last_mass = planetoid.mass
		while True:
			new_dust_mass, new_gas_mass = self.collect_dust( planetoid )
			planetoid.dust_mass = new_dust_mass
			planetoid.gas_mass = new_gas_mass
			print (planetoid.mass - last_mass) / last_mass
			if (planetoid.mass - last_mass) < (0.0001 * last_mass): # Accretion has slowed enough. Stop trying.
				break
			last_mass = planetoid.mass
		print "Accretion halted at ",planetoid.mass
		self.update_dust_lanes( planetoid )

class Planetoid:
	def __init__( self, a, e, dust_mass, gas_mass ):
		self.a = a
		self.e = e
		self.dust_mass = dust_mass
		self.gas_mass = gas_mass
	
	@property
	def mass(self):
		return self.dust_mass + self.gas_mass
		
	@property
	def reduced_mass(self):
		# To understand what this is all about...
		# http://spiff.rit.edu/classes/phys440/lectures/reduced/reduced.html
		# But some sort of 3 body case, see dole.
		# TODO: Understand better?
		return (self.mass / (1.0 + self.mass)) ** 0.25;
		
	@property
	def inner_effect_limit(self):
		temp = (self.a * (1.0 - self.e) * (1.0 - self.mass) / (1.0 + DISK_ECCENTRICITY))
		if temp < 0:
			return 0
		return temp

	@property
	def outer_effect_limit(self):
		return (self.a * (1.0 + self.e) * (1.0 + self.mass) / (1.0 - DISK_ECCENTRICITY))
		
class Planetesimal(Planetoid):
	def __init__( self, disk, a, e, dust_mass, gas_mass ):
		Planetoid.__init__(self, a, e, dust_mass, gas_mass)
		self.disk = disk

	@property
	def critical_mass(self):
		perihelion_dist = self.a * (1.0 - self.e);
		temp = perihelion_dist * sqrt( self.disk.star.luminosity_ratio )
		return B * ( temp ** -0.75 )

def random_planetesimal( disk ):
	a = random.uniform( disk.planet_inner_bound, disk.planet_outer_bound )
	e = 1.0 - ( random.uniform(0.0, 1.0) ** ECCENTRICITY_COEFF )
	if e > .99:
		e = .99
	return Planetesimal( disk, a, e, PROTOPLANET_MASS, 0 )

def dist_planetary_masses( star, inner_dust, outer_dust, do_moons = True ):
	disk = CircumstellarDisk(star)

	planets = []
	
	sequential_failures = 0

	while disk.dust_left and sequential_failures < 10**3:
		canidate = random_planetesimal(disk)
		
		#logging.info("Checking " + str(canidate.a) + " AU.")
			
		if disk.dust_available(canidate.inner_effect_limit, canidate.outer_effect_limit) > 0: 
			sequential_failures = 0
			logging.info("Injecting planetesimal at " + str(canidate.a) + " AU ...");
			
			disk.accrete_dust(canidate)
			
			if canidate.mass > PROTOPLANET_MASS:
				coalesce_planetesimals( disk, planets, canidate, do_moons )
				logging.info( "\tsuccess." )
			else:
				logging.info( "\tfailed due to large neighbor." )
		else:
			sequential_failures += 1
			#logging.info( "\tfailed, no dust in region." )
	return planets

class Protoplanet(Planetoid):
	def __init__( self, star, a, e, dust_mass, gas_mass ):
		Planetoid.__init__( self, a, e, dust_mass, gas_mass )
		self.star = star
		self.moons = []
	def add_moon( self, moon ):
		self.moons.append( moon )
		
	@property
	def mass_of_moons(self):
		return sum([ moon.mass for moon in self.moons ])
		
	@property
	def critical_mass(self):
		perihelion_dist = self.a * (1.0 - self.e);
		temp = perihelion_dist * sqrt( self.star.luminosity_ratio )
		return B * ( temp ** -0.75 )
		
	def __repr__(self):
		def mass_repr():
			if self.mass * SUN_MASS_IN_MOON_MASSES <= 50:
				return str( self.mass * SUN_MASS_IN_MOON_MASSES ) + " M_moon"
			if self.mass * SUN_MASS_IN_EARTH_MASSES <= 50:
				return str( self.mass * SUN_MASS_IN_EARTH_MASSES ) + " M_earth"
			return str( self.mass * SUN_MASS_IN_JUPITER_MASSES ) + " M_jupiter"
			
		return "\tMass: " +  mass_repr() + "; Orbit: " + str(self.a) + " AU, Moons: " + str(len(self.moons)) + "\n"

class Protomoon(Planetoid):
	def __init__( self, protoplanet, dust_mass, gas_mass ):
		Planetoid.__init__(self, None, None, dust_mass, gas_mass)
		self.protoplanet = protoplanet
		
def convert_planetesimal_to_protoplanet( planetesimal ):
	return Protoplanet( planetesimal.disk.star, planetesimal.a, planetesimal.e, planetesimal.dust_mass, planetesimal.gas_mass )
	
def convert_planetesimal_to_protomoon( planetesimal, planet ):
	print "GOT HERE"
	return Protomoon( planet, planetesimal.dust_mass, planetesimal.gas_mass )

def coalesce_planetesimals( disk, planets, canidate, do_moons ):
	finished = False

	# First we try to find an existing planet with an over-lapping orbit.
	for planet in planets:
	
		diff = planet.a - canidate.a
		
		if diff > 0.0:
			dist1 = (canidate.a * (1.0 + canidate.e) * (1.0 + canidate.reduced_mass)) - canidate.a;
			# x aphelion
			dist2 = planet.a - (planet.a * (1.0 - planet.e) * (1.0 - planet.reduced_mass));
		else:
			dist1 = canidate.a - (canidate.a * (1.0 - canidate.e) * (1.0 - canidate.reduced_mass));
			# x perihelion
			dist2 = (planet.a * (1.0 + planet.e) * (1.0 + planet.reduced_mass)) - planet.a;
		
		if abs(diff) <= abs(dist1) or abs(diff) <= abs(dist2):
			# Figure out the new orbit.
			a = (planet.mass + canidate.mass) / ((planet.mass / planet.a) + (canidate.mass / canidate.a));
			
			temp = planet.mass * sqrt(planet.a) * sqrt( 1.0 - ( planet.e ** 2.0 ) )
			temp = temp + ( canidate.mass * sqrt( canidate.a ) * sqrt(sqrt(1.0 - ( canidate.e ** 2.0 ) )))
			temp = temp / (( planet.mass + canidate.mass ) * sqrt( canidate.a ))
			temp = 1.0 - ( temp ** 2.0 )
			if temp < 0.0 or temp >= 1.0:
				temp = 0.0
			e = sqrt(temp)
			
			if do_moons:
				if canidate.mass < canidate.critical_mass:
					if canidate.mass * SUN_MASS_IN_EARTH_MASSES < 2.5 and canidate.mass * SUN_MASS_IN_EARTH_MASSES > .0001 and planet.mass_of_moons < planet.mass * .05 and planet.mass > canidate.mass:
						# TODO: Remove planet.mass > canidate.mass distinction, just switch the canidate and planet!
						planet.add_moon( convert_planetesimal_to_protomoon( canidate, planet) )
						logging.info("Moon captured at " + str(planet.a) + " AU. Planet Mass: " + str(planet.mass * SUN_MASS_IN_EARTH_MASSES) + " earth masses; Moon Mass: " + str(canidate.mass * SUN_MASS_IN_EARTH_MASSES) + " earth masses." )
						finished = True;
						break;
					else:
						logging.info("Did not capture potential moon at " + str(planet.a) + " AU. Collision imminent.") # TODO: Reasons.
						
			logging.info("Collision between two planetesimals! Computing new orbit and accumulating additional mass.")
			temp = planet.mass + canidate.mass;
			disk.accrete_dust(planet); # Accrete MORE DUST! TODO: Refactor to this.

			planet.a = a;
			planet.e = e;
			planet.mass = temp;
			planet.dust_mass = planet.dust_mass + canidate.dust_mass # + new_dust
			planet.gas_mass  = planet.gas_mass + canidate.gas_mass # + new_gas
			finished = True;
			logging.info("Conglomerate is now " + str(planet.mass * SUN_MASS_IN_EARTH_MASSES) + " earth masses at " + str( planet.a ) + " AU.")
			
	if not finished:
		logging.info("New Protoplanet at " + str(canidate.a) + "AU.") # TODO: Extra info.
		planets.append( convert_planetesimal_to_protoplanet( canidate ) )


def generate_planets( star, flag_char, do_gasses, do_moons ):
	logging.warning("generate_planets( ... ) not implemented yet.") # TODO
	return


###
# Smoke Test
###

generate_stellar_system(
		Star(
			1.0, # Mass Ratio
			4.6 * (10**9), # Age
		)
	)
