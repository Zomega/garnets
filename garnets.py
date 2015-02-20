import logging
logging.getLogger().setLevel(logging.INFO)

import random

from math import sqrt, exp

###
# CONSTANTS
###

DUST_DENSITY_COEFF = 0.002
ECCENTRICITY_COEFF = 0.077
PROTOPLANET_MASS = 10.0**-15 # Units of solar masses
ALPHA = 5.0
B = 1.2 * 10**-5
N = 3.0

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
		return 200.0 * ( self.mass_ratio ** 0.3333 );

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
	age = random.randrange(1 *10**9, 6*10**9)
	mass = 1
	
	

def generate_stellar_system( star, do_gases = True, do_moons = True ):
	protoplanets = dist_planetary_masses( star, 0.0, star.stellar_dust_limit, do_moons)
	flag_char = None # TODO: Remove / replace
	system = generate_planets( star, flag_char, do_gases, do_moons)
	return system

# Create protoplanets.

class CircumstellarDisk: # TODO: Everything. Dust Lanes...
	def __init__( self, star ):
		self.star = star
		self.planet_inner_bound = 0.3 * ( star.mass_ratio ** 0.333 )
		self.planet_outer_bound = 50  * ( star.mass_ratio ** 0.333 )
		self.eccentricity = 0.2

	@property
	def dust_density(self, a):
		return DUST_DENSITY_COEFF * sqrt( star.mass_ratio ) * exp( -ALPHA * ( a ** (1.0 / N) ) )

	@property # TODO: Do this properly.
	def dust_left(self):
		if random.uniform(0.0, 1.0) > 0.01:
			return True
		return False

	def dust_available(self, inner, outer):
		return 1.0 # TODO

	def collect_dust(self, planetesimal):
		return 0 # TODO

	def update_dust_lanes(self, planetesimal):
		return # TODO

class Planetesimal:
	def __init__( self, disk, a, e, mass, dust_mass = 0, gas_mass = 0 ):
		self.disk = disk
		self.a = a
		self.e = e
		self.mass = mass
		self.dust_mass = dust_mass
		self.gas_mass = gas_mass

	@property
	def inner_effect_limit(self):
		return (self.a * (1.0 - self.e) * (1.0 - self.mass) / (1.0 + self.disk.eccentricity))

	@property
	def outer_effect_limit(self):
		return (self.a * (1.0 + self.e) * (1.0 + self.mass) / (1.0 - self.disk.eccentricity));

	@property
	def critical_limit(self):
		perihelion_dist = self.a * (1.0 - self.e);
		temp = perihelion_dist * sqrt( self.disk.star.luminosity_ratio );
		return B * ( temp ** -0.75 );

	def accrete_dust(self):
		last_mass = self.mass
		while True:
			self.mass += self.disk.collect_dust( self ) # TODO: Rewrite to delta for better numerics.
								# TODO: understand exactly what collect_dust does, tweak accordingly.
			if (self.mass - last_mass) < (0.0001 * last_mass): # Accretion has slowed enough. Stop trying.
				break
		self.disk.update_dust_lanes( self )

def random_planetesimal( disk ):
	a = random.uniform( disk.planet_inner_bound, disk.planet_outer_bound )
	e = 1.0 - ( random.uniform(0.0, 1.0) ** ECCENTRICITY_COEFF )
	if e > .99:
		e = .99
	mass = PROTOPLANET_MASS
	return Planetesimal( disk, a, e, mass )

def dist_planetary_masses( star, inner_dust, outer_dust, do_moons = True ):
	disk = CircumstellarDisk(star)

	planets = []

	def random_semimajor_axis():
		a = random.uniform( planet_inner_bound, planet_outer_bound )
		return a
	def random_eccentricity():
		e = 1.0 - ( random.uniform(0.0, 1.0) ** ECCENTRICITY_COEFF )
	
		if e > .99:
			e = .99
		return e

	while disk.dust_left:
		canidate = random_planetesimal(disk)
		
		logging.info("Checking " + str(canidate.a) + " AU.")
			
		if disk.dust_available(canidate.inner_effect_limit, canidate.outer_effect_limit) > 0: 
			logging.info("Injecting planetesimal at " + str(canidate.a) + " AU ...");
			
			canidate.accrete_dust()
			
			canidate.dust_mass += PROTOPLANET_MASS;
			
			if canidate.mass > PROTOPLANET_MASS:
				coalesce_planetesimals( planets, canidate, do_moons )
				logging.info( "\tsuccess." )
			else:
				logging.info( "\tfailed due to large neighbor." )
		else:
			logging.info( "\tfailed, no dust in region." )
	return

class Protoplanet:
	def __init__( self, star, a, e, mass, dust_mass, gas_mass ):
		self.star = star
		self.a = a
		self.e = e
		self.mass = mass
		self.dust_mass = dust_mass
		self.gas_mass = gas_mass
		self.moons = []
	def add_moon( moon ):
		self.moons.append( moon )

class Protomoon:
	def __init( self, protoplanet, mass, dust_mass, gas_mass ):
		self.protoplanet = protoplanet
		self.mass = mass
		self.dust_mass = mass
		self.gas_mass = mass

def coalesce_planetesimals( planets, canidate, do_moons ):
	finished = False

	def overlapping( planet, canidate ):
		# TODO

	# First we try to find an existing planet with an over-lapping orbit.
	for planet in planets:
		if overlapping( planet, canidate ):
			# Figure out the new e / a
			# TODO:
			if do_moons:
				if capture_moon( planet, canidate ):
					planet.add_moon( convert_planetesimal_to_protomoon( canidate, planet) )
					logging.info("Moon captured at " + str(planet.a) + " AU. Planet Mass: " + str(planet.mass * SUN_MASS_IN_EARTH_MASSES) + " earth masses; Moon Mass: " + str(canidate.mass * SUN_MASS_IN_EARTH_MASSES) + " earth masses.")
					finished = True;
					break;
				else:
					logging.info("Did not capture moon at " + str(planet.a) + " AU. Collision imminent.") # TODO: Reasons.
			logging.info("Collision between two planetesimals! Computing new orbit and accumulating additional mass.") # TODO: Extra info.
			
	if not finished:
		# Planetesimals didn't collide. Make it a planet.
		planets.append( convert_planetesimal_to_protoplanet( canidate ) )
		# TODO: Sort Planets?
		

'''void coalesce_planetesimals(long double a, long double e, long double mass, long double crit_mass,
							long double dust_mass, long double gas_mass,
							long double stell_luminosity_ratio,
							long double body_inner_bound, long double body_outer_bound,
							int			do_moons)
{
	planet_pointer	the_planet;
	planet_pointer	next_planet;
	planet_pointer	prev_planet;
	int 			finished; 
	long double 	temp;
	long double 	diff;
	long double 	dist1;
	long double 	dist2;
	
	finished = FALSE;
	prev_planet = NULL;

// First we try to find an existing planet with an over-lapping orbit.
	
	for (the_planet = planet_head;
		 the_planet != NULL;
		 the_planet = the_planet->next_planet)
	{
		diff = the_planet->a - a;
		
		if ((diff > 0.0))
		{
			dist1 = (a * (1.0 + e) * (1.0 + reduced_mass)) - a;
			/* x aphelion	 */
			reduced_mass = pow((the_planet->mass / (1.0 + the_planet->mass)),(1.0 / 4.0));
			dist2 = the_planet->a
				- (the_planet->a * (1.0 - the_planet->e) * (1.0 - reduced_mass));
		}
		else 
		{
			dist1 = a - (a * (1.0 - e) * (1.0 - reduced_mass));
			/* x perihelion */
			reduced_mass = pow((the_planet->mass / (1.0 + the_planet->mass)),(1.0 / 4.0));
			dist2 = (the_planet->a * (1.0 + the_planet->e) * (1.0 + reduced_mass))
				- the_planet->a;
		}
		
		if (((fabs(diff) <= fabs(dist1)) || (fabs(diff) <= fabs(dist2))))
		{
			long double new_dust = 0;
			long double	new_gas = 0;
			long double new_a = (the_planet->mass + mass) / 
								((the_planet->mass / the_planet->a) + (mass / a));
			
			temp = the_planet->mass * sqrt(the_planet->a) * sqrt(1.0 - pow(the_planet->e,2.0));
			temp = temp + (mass * sqrt(a) * sqrt(sqrt(1.0 - pow(e,2.0))));
			temp = temp / ((the_planet->mass + mass) * sqrt(new_a));
			temp = 1.0 - pow(temp,2.0);
			if (((temp < 0.0) || (temp >= 1.0)))
				temp = 0.0;
			e = sqrt(temp);
			
			if (do_moons)
			{
				long double existing_mass = 0.0;
				
				if (the_planet->first_moon != NULL)
				{
					planet_pointer	m;
					
					for (m = the_planet->first_moon;
						 m != NULL;
						 m = m->next_planet)
					{
						existing_mass += m->mass;
					}
				}

				if (mass < crit_mass)
				{
					if ((mass * SUN_MASS_IN_EARTH_MASSES) < 2.5
					 && (mass * SUN_MASS_IN_EARTH_MASSES) > .0001
					 && existing_mass < (the_planet->mass * .05)
					   )
					{
						planet_pointer	the_moon = (planets *)malloc(sizeof(planets));
						
						the_moon->type 			= tUnknown;
	/* 					the_moon->a 			= a; */
	/* 					the_moon->e 			= e; */
						the_moon->mass 			= mass;
						the_moon->dust_mass 	= dust_mass;
						the_moon->gas_mass 		= gas_mass;
						the_moon->atmosphere 	= NULL;
						the_moon->next_planet 	= NULL;
						the_moon->first_moon 	= NULL;
						the_moon->gas_giant 	= FALSE;
						the_moon->atmosphere	= NULL;
						the_moon->albedo		= 0;
						the_moon->gases			= 0;
						the_moon->surf_temp		= 0;
						the_moon->high_temp		= 0;
						the_moon->low_temp		= 0;
						the_moon->max_temp		= 0;
						the_moon->min_temp		= 0;
						the_moon->greenhs_rise	= 0;
						the_moon->minor_moons 	= 0;
	
						if ((the_moon->dust_mass + the_moon->gas_mass)
						  > (the_planet->dust_mass + the_planet->gas_mass))
						{
							long double	temp_dust = the_planet->dust_mass;
							long double temp_gas  = the_planet->gas_mass;
							long double temp_mass = the_planet->mass;
							
							the_planet->dust_mass = the_moon->dust_mass;
							the_planet->gas_mass  = the_moon->gas_mass;
							the_planet->mass      = the_moon->mass;
							
							the_moon->dust_mass   = temp_dust;
							the_moon->gas_mass    = temp_gas;
							the_moon->mass        = temp_mass;
						}
	
						if (the_planet->first_moon == NULL)
							the_planet->first_moon = the_moon;
						else
						{
							the_moon->next_planet = the_planet->first_moon;
							the_planet->first_moon = the_moon;
						}
						
						finished = TRUE;
						
						if (flag_verbose & 0x0100)
							fprintf (stderr, "Moon Captured... "
									 "%5.3Lf AU (%.2LfEM) <- %.2LfEM\n",
									the_planet->a, the_planet->mass * SUN_MASS_IN_EARTH_MASSES, 
									mass * SUN_MASS_IN_EARTH_MASSES
									);
					}
					else 
					{
						if (flag_verbose & 0x0100)
							fprintf (stderr, "Moon Escapes... "
									 "%5.3Lf AU (%.2LfEM)%s %.2LfEM%s\n",
									the_planet->a, the_planet->mass * SUN_MASS_IN_EARTH_MASSES, 
									existing_mass < (the_planet->mass * .05) ? "" : " (big moons)",
									mass * SUN_MASS_IN_EARTH_MASSES,
									(mass * SUN_MASS_IN_EARTH_MASSES) >= 2.5 ? ", too big" : 
									  (mass * SUN_MASS_IN_EARTH_MASSES) <= .0001 ? ", too small" : ""
									);
					}
				}
			}

			if (!finished)
			{
				if (flag_verbose & 0x0100)
						fprintf (stderr, "Collision between two planetesimals! "
								"%4.2Lf AU (%.2LfEM) + %4.2Lf AU (%.2LfEM = %.2LfEMd + %.2LfEMg [%.3LfEM])-> %5.3Lf AU (%5.3Lf)\n",
								the_planet->a, the_planet->mass * SUN_MASS_IN_EARTH_MASSES, 
								a, mass * SUN_MASS_IN_EARTH_MASSES, 
								dust_mass * SUN_MASS_IN_EARTH_MASSES, gas_mass * SUN_MASS_IN_EARTH_MASSES, 
								crit_mass * SUN_MASS_IN_EARTH_MASSES,
								new_a, e);
			
				temp = the_planet->mass + mass;
				accrete_dust(&temp, &new_dust, &new_gas,
							 new_a,e,stell_luminosity_ratio,
							 body_inner_bound,body_outer_bound);
	
				the_planet->a = new_a;
				the_planet->e = e;
				the_planet->mass = temp;
				the_planet->dust_mass += dust_mass + new_dust;
				the_planet->gas_mass += gas_mass + new_gas;
				if (temp >= crit_mass)
					the_planet->gas_giant = TRUE;
					
				while (the_planet->next_planet != NULL && the_planet->next_planet->a < new_a)
				{
					next_planet = the_planet->next_planet;
					
					if (the_planet == planet_head)
						planet_head = next_planet;
					else
						prev_planet->next_planet = next_planet;
					
					the_planet->next_planet = next_planet->next_planet;
					next_planet->next_planet = the_planet;
					prev_planet = next_planet;
				}
			}

			finished = TRUE;
			break;
		}
		else 
		{
			prev_planet = the_planet;
		}
	}
	
	if (!(finished))			// Planetesimals didn't collide. Make it a planet.
	{
		the_planet = (planets *)malloc(sizeof(planets));
		
		the_planet->type 			= tUnknown;
		the_planet->a 				= a;
		the_planet->e 				= e;
		the_planet->mass 			= mass;
		the_planet->dust_mass 		= dust_mass;
		the_planet->gas_mass 		= gas_mass;
		the_planet->atmosphere 		= NULL;
		the_planet->first_moon 		= NULL;
		the_planet->atmosphere		= NULL;
		the_planet->albedo			= 0;
		the_planet->gases			= 0;
		the_planet->surf_temp		= 0;
		the_planet->high_temp		= 0;
		the_planet->low_temp		= 0;
		the_planet->max_temp		= 0;
		the_planet->min_temp		= 0;
		the_planet->greenhs_rise	= 0;
		the_planet->minor_moons 	= 0;
		
		if ((mass >= crit_mass))
			the_planet->gas_giant = TRUE;
		else 
			the_planet->gas_giant = FALSE;
		
		if ((planet_head == NULL))
		{
			planet_head = the_planet;
			the_planet->next_planet = NULL;
		}
		else if ((a < planet_head->a))
		{
			the_planet->next_planet = planet_head;
			planet_head = the_planet;
		}
		else if ((planet_head->next_planet == NULL))
		{
			planet_head->next_planet = the_planet;
			the_planet->next_planet = NULL;
		}
		else 
		{
			next_planet = planet_head;
			while (((next_planet != NULL) && (next_planet->a < a)))
			{
				prev_planet = next_planet;
				next_planet = next_planet->next_planet;
			}
			the_planet->next_planet = next_planet;
			prev_planet->next_planet = the_planet;
		}
	}
}'''

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
