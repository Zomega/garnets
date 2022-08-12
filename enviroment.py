import numpy as np
from enum import Enum
from math import sqrt, pi, cos, fabs, exp, log
from constants import SOLAR_MASS_IN_GRAMS, SUN_MASS_IN_EARTH_MASSES

from math import inf as INCREDIBLY_LARGE_NUMBER

# Universal constants
from constants import GRAV_CONSTANT
from constants import MOLAR_GAS_CONST

# Import conversion factors
from constants import CM_PER_KM, CM_PER_METER, SECONDS_PER_HOUR, DAYS_IN_A_YEAR, RADIANS_PER_ROTATION, MILLIBARS_PER_BAR

# Import Earth related constants.
from constants import EARTH_RADIUS, EARTH_DENSITY, EARTH_MASS_IN_GRAMS, EARTH_AXIAL_TILT, EARTH_AVERAGE_KELVIN, EARTH_CONVECTION_FACTOR, EARTH_SURF_PRES_IN_MILLIBARS, EARTH_ACCELERATION, EARTH_EFFECTIVE_TEMP, EARTH_WATER_MASS_PER_AREA, KM_EARTH_RADIUS, CHANGE_IN_EARTH_ANG_VEL

# Atmospheric Chemistry stuff
from constants import CLOUD_COVERAGE_FACTOR, GAS_RETENTION_THRESHOLD
from constants import FREEZING_POINT_OF_WATER
from constants import AN_O
from constants import MOL_HYDROGEN, MOL_NITROGEN, ATOMIC_NITROGEN
from constants import WATER_VAPOR
from constants import MIN_O2_IPP, MAX_O2_IPP, H20_ASSUMED_PRESSURE
from constants import EARTH_ALBEDO, ICE_ALBEDO, CLOUD_ALBEDO, AIRLESS_ICE_ALBEDO, GREENHOUSE_TRIGGER_ALBEDO, ROCKY_ALBEDO, ROCKY_AIRLESS_ALBEDO, WATER_ALBEDO

# Tunable constants?
from constants import J

from tabulate import tabulate

from util import pow1_4, pow2, pow3, about

# TODO(woursler): Break this file up.

# TODO(woursler): This whole file desperately needs natu.

VERBOSE = False


class BreathabilityPhrase(Enum):
    NONE = 0
    BREATHABLE = 1
    UNBREATHABLE = 2
    POISONOUS = 3


class PlanetType(Enum):
    UNKNOWN = 0
    ROCK = 1
    VENUSIAN = 2
    TERRESTRIAL = 3
    SUB_SUB_GAS_GIANT = 4
    SUB_GAS_GIANT = 5
    GAS_GIANT = 6
    MARTIAN = 7
    WATER = 8
    ICE = 9
    ASTEROIDS = 10
    # TODO(woursler): Don't know what this means... maybe tidally locked?
    ONE_FACE = 11


class Zone(Enum):  # TODO(woursler): Figure it out. Might be related to habitable zone?
    ZONE_1 = 1
    ZONE_2 = 2
    ZONE_3 = 3


def orb_zone(luminosity, orb_radius):
    '''The orbital 'zone' of the particle.'''
    if orb_radius < (4.0 * sqrt(luminosity)):
        return Zone.ZONE_1
    elif orb_radius < (15.0 * sqrt(luminosity)):
        return Zone.ZONE_2
    else:
        return Zone.ZONE_3


def volume_radius(mass, density):
    '''The mass is in units of solar masses, the density is in units
    of grams/cc.  The radius returned is in units of km.'''

    mass = mass * SOLAR_MASS_IN_GRAMS
    volume = mass / density
    radius_in_cm = ((3.0 * volume) / (4.0 * pi)) ** (1.0 / 3.0)
    return radius_in_cm / CM_PER_KM


# These constants are specific to kothari_radius.
# All units are in cgs system, ie: cm, g, dynes, etc.
A1_20 = 6.485E12
A2_20 = 4.0032E-8
BETA_20 = 5.71E12
JIMS_FUDGE = 1.004


def kothari_radius(mass, giant, zone):
    '''Returns the radius of the planet in kilometers.

    The mass passed in is in units of solar masses.
    This formula is listed as eq.9 in Fogg's article, some typos
    crop up in that eq.  See "The Internal Constitution of Planets", by
    Dr. D. S. Kothari, Mon. Not. of the Royal Astronomical Society, 96
    pp.833-843, for the derivation.  Specifically, is Kothari's
    eq.23, appears on page 840.'''

    if zone == Zone.ZONE_1:
        if giant:
            atomic_weight = 9.5
            atomic_num = 4.5

        else:
            atomic_weight = 15.0
            atomic_num = 8.0

    else:
        if zone == Zone.ZONE_2:
            if giant:
                atomic_weight = 2.47
                atomic_num = 2.0

            else:
                atomic_weight = 10.0
                atomic_num = 5.0

        else:
            if giant:
                atomic_weight = 7.0
                atomic_num = 4.0

            else:
                atomic_weight = 10.0
                atomic_num = 5.0

    temp1 = atomic_weight * atomic_num

    temp = (2.0 * BETA_20 * (SOLAR_MASS_IN_GRAMS ** (1.0 / 3.0))) / \
        (A1_20 * (temp1 ** (1.0 / 3.0)))

    temp2 = A2_20 * (atomic_weight ** (4.0 / 3.0)) * \
        (SOLAR_MASS_IN_GRAMS ** (2.0 / 3.0))
    temp2 = temp2 * (mass ** (2.0 / 3.0))
    temp2 = temp2 / (A1_20 * (atomic_num ** 2.0))   #Changed by the Seans, 2/23 to float 2.0
    temp2 = 1.0 + temp2
    temp = temp / temp2
    temp = (temp * (mass ** (1.0 / 3.0))) / CM_PER_KM

    temp = temp / JIMS_FUDGE

    return(temp)


def empirical_density(mass, orb_radius, r_ecosphere, gas_giant):
    '''The mass passed in is in units of solar masses, the orbital radius
    is in units of AU.  The density is returned in units of grams/cc.'''

    temp = (mass * SUN_MASS_IN_EARTH_MASSES) ** (1.0 / 8.0)
    temp = temp * (r_ecosphere / orb_radius) ** (1.0 / 4.0)
    if gas_giant:
        return(temp * 1.2)
    else:
        return(temp * 5.5)


def volume_density(mass, equat_radius):
    '''The mass passed in is in units of solar masses, the equatorial
    radius is in km.  The density is returned in units of grams/cc.'''

    mass = mass * SOLAR_MASS_IN_GRAMS
    equat_radius = equat_radius * CM_PER_KM
    volume = (4.0 * pi * (equat_radius ** 3)) / 3.0
    return(mass / volume)


def period(separation, small_mass, large_mass):
    '''The separation is in units of AU, both masses are in units of solar
    masses.   The period returned is in terms of Earth days.'''

    period_in_years = sqrt((separation ** 3) / (small_mass + large_mass))
    return(period_in_years * DAYS_IN_A_YEAR)


def day_length(planet):
    '''Fogg's information for this routine came from Dole "Habitable Planets
    for Man", Publishing Company, NY, 1964.  From this, he came
    up with his eq.12, is the equation for the 'base_angular_velocity'
    below.  He then used an equation for the change in angular velocity per
    time (dw/dt) from P. Goldreich and S. Soter's paper "Q in the Solar
    System" in Icarus, 5, pp.375-389 (1966).   Using as a comparison the
    change in angular velocity for the Earth, has come up with an
    approximation for our planet (his eq.13) and take that into account.
    This is used to find 'change_in_angular_velocity' below.

    Input parameters are mass (in solar masses), radius (in Km), orbital
    period (in days), radius (in AU), density (in g/cc),
    eccentricity, whether it is a gas giant or not.
    The length of the day is returned in units of hours.'''

    planetary_mass_in_grams = planet.mass * SOLAR_MASS_IN_GRAMS
    equatorial_radius_in_cm = planet.radius * CM_PER_KM
    year_in_hours = planet.orb_period * 24.0
    giant = (planet.type == PlanetType.GAS_GIANT or
             planet.type == PlanetType.SUB_GAS_GIANT or
             planet.type == PlanetType.SUB_SUB_GAS_GIANT)

    stopped = False

    planet.resonant_period = False  # Warning: Modifies the planet

    if giant:
        k2 = 0.24
    else:
        k2 = 0.33

    base_angular_velocity = sqrt(2.0 * J * (planetary_mass_in_grams) /
                                 (k2 * (equatorial_radius_in_cm ** 2)))

    # This next calculation determines how much the planet's rotation is
    # slowed by the presence of the star.

    change_in_angular_velocity = CHANGE_IN_EARTH_ANG_VEL * (planet.density / EARTH_DENSITY) * (equatorial_radius_in_cm / EARTH_RADIUS) * (
        EARTH_MASS_IN_GRAMS / planetary_mass_in_grams) * (planet.sun.mass_ratio ** 2.0) * (1.0 / (planet.orbit.a ** 6.0))
    ang_velocity = base_angular_velocity + \
        (change_in_angular_velocity * planet.sun.age)

    # Now we change from rad/sec to hours/rotation.

    if ang_velocity <= 0.0:
        stopped = True
        day_in_hours = INCREDIBLY_LARGE_NUMBER

    else:
        day_in_hours = RADIANS_PER_ROTATION / (SECONDS_PER_HOUR * ang_velocity)

    if (day_in_hours >= year_in_hours) or stopped:
        if planet.orbit.e > 0.1:
            spin_resonance_factor = (1.0 - planet.orbit.e) / (1.0 + planet.orbit.e)
            planet.resonant_period = True
            return(spin_resonance_factor * year_in_hours)

        else:
            return(year_in_hours)

    return(day_in_hours)


def inclination(orb_radius):
    '''The orbital radius is expected in units of Astronomical Units (AU).
    Inclination is returned in units of degrees. '''
    temp = int((orb_radius ** 0.2) * about(EARTH_AXIAL_TILT, 0.4))
    return temp % 360


def escape_vel(mass, radius):
    '''This function implements the escape velocity calculation.  Note that
    it appears that Fogg's eq.15 is incorrect.
    The mass is in units of solar mass, radius in kilometers, the
    velocity returned is in cm/sec. '''
    mass_in_grams = mass * SOLAR_MASS_IN_GRAMS
    radius_in_cm = radius * CM_PER_KM
    return sqrt(2.0 * GRAV_CONSTANT * mass_in_grams / radius_in_cm)


def rms_vel(molecular_weight, exospheric_temp):
    '''This is Fogg's eq.16.  The molecular weight (usually assumed to be N2)
    is used as the basis of the Root Mean Square (RMS) velocity of the
    molecule or atom.  The velocity returned is in cm/sec.
    Orbital radius is in A.U.(ie: in units of the earth's orbital radius).'''
    return sqrt((3.0 * MOLAR_GAS_CONST * exospheric_temp) / molecular_weight) * CM_PER_METER


def molecule_limit(mass, equat_radius, exospheric_temp):
    '''This function returns the smallest molecular weight retained by the
    body, is useful for determining the atmosphere composition.
    Mass is in units of solar masses, equatorial radius is in units of
    kilometers. '''
    esc_velocity = escape_vel(mass, equat_radius)

    return ((3.0 * MOLAR_GAS_CONST * exospheric_temp) /
            (pow2((esc_velocity / GAS_RETENTION_THRESHOLD) / CM_PER_METER)))


def acceleration(mass, radius):
    '''This function calculates the surface acceleration of a planet.   The
    mass is in units of solar masses, radius in terms of km, the
    acceleration is returned in units of cm/sec2. '''

    return GRAV_CONSTANT * (mass * SOLAR_MASS_IN_GRAMS) / pow2(radius * CM_PER_KM)


def gravity(acceleration):
    '''This function calculates the surface gravity of a planet.  The
    acceleration is in units of cm/sec2, the gravity is returned in
    units of Earth gravities. '''

    return acceleration / EARTH_ACCELERATION


def vol_inventory(mass, escape_vel, rms_vel, stellar_mass, zone, greenhouse_effect, accreted_gas):
    '''This implements Fogg's eq.17.  The 'inventory' returned is unitless.'''

    velocity_ratio = escape_vel / rms_vel
    if velocity_ratio >= GAS_RETENTION_THRESHOLD:
        if zone == Zone.ZONE_1:
            proportion_ = 140000.0
            '''100 . 140 JLB'''
        elif zone == Zone.ZONE_2:
            proportion_ = 75000.0
        elif zone == Zone.ZONE_3:
            proportion_ = 250.0
        else:
            raise NotImplementedError("orbital zone not initialized correctly")

        earth_units = mass * SUN_MASS_IN_EARTH_MASSES
        temp1 = (proportion_ * earth_units) / stellar_mass
        temp2 = about(temp1, 0.2)
        temp2 = temp1
        if greenhouse_effect or accreted_gas:
            return temp2
        else:
            return temp2 / 140.0  # 100 . 140 JLB

    else:
        return 0.0


def pressure(volatile_gas_inventory, equat_radius, gravity):
    '''This implements Fogg's eq.18.  The pressure returned is in units of
    millibars (mb).   The gravity is in units of Earth gravities, radius
    in units of kilometers.

    JLB: Aparently this assumed that pressure = 1000mb. I've added a
    fudge factor (EARTH_SURF_PRES_IN_MILLIBARS / 1000.) to correct for that'''

    equat_radius = KM_EARTH_RADIUS / equat_radius
    return volatile_gas_inventory * gravity * (EARTH_SURF_PRES_IN_MILLIBARS / 1000.) / (equat_radius ** 2)


def boiling_point(surf_pressure):
    '''This function returns the boiling point of water in an atmosphere of
    pressure 'surf_pressure', in millibars.  The boiling point is
    returned in units of Kelvin.  This is Fogg's eq.21. '''

    surface_pressure_in_bars = surf_pressure / MILLIBARS_PER_BAR
    return 1.0 / ((log(surface_pressure_in_bars) / -5050.5) + (1.0 / 373.0))


def hydro_fraction(volatile_gas_inventory, planet_radius):
    '''This function is Fogg's eq.22.   Given the volatile gas inventory and
    planetary radius of a planet (in Km), function returns the
    fraction of the planet covered with water.
    I have changed the function very slightly:   the fraction of Earth's
    surface covered by water is 71%, not 75% as Fogg used. '''

    temp = (0.71 * volatile_gas_inventory / 1000.0) * \
        ((KM_EARTH_RADIUS / planet_radius) ** 2)
    if temp >= 1.0:
        return 1.0
    else:
        return temp


# Constant only used here and not really explained.
Q2_36 = 0.0698  # 1/Kelvin


def cloud_fraction(surf_temp, smallest_MW_retained, equat_radius, hydro_fraction):
    '''Given the surface temperature of a planet (in Kelvin), function
    returns the fraction of cloud cover available.   This is Fogg's eq.23.
    See Hart in "Icarus" (vol 33, pp23 - 39, 1978) for an explanation.
    This equation is Hart's eq.3.
    I have modified it slightly using constants and relationships from
    Glass's book "Introduction to Planetary Geology", p.46.
    The 'CLOUD_COVERAGE_FACTOR' is the amount of surface area on Earth
    covered by one Kg. of cloud.'''
    if smallest_MW_retained > WATER_VAPOR:
        return 0.0
    else:
        surf_area = 4.0 * pi * (equat_radius ** 2)
        hydro_mass = hydro_fraction * surf_area * EARTH_WATER_MASS_PER_AREA
        water_vapor_in_kg = (0.00000001 * hydro_mass) * \
            np.exp(Q2_36 * (surf_temp - EARTH_AVERAGE_KELVIN))
        fraction = CLOUD_COVERAGE_FACTOR * water_vapor_in_kg / surf_area
        if fraction >= 1.0:
            return 1.0
        else:
            return fraction


def ice_fraction(hydro_fraction, surf_temp):
    '''Given the surface temperature of a planet (in Kelvin), function
    returns the fraction of the planet's surface covered by ice.  This is
    Fogg's eq.24.  See Hart[24] in Icarus vol.33, p.28 for an explanation.
    I have changed a constant from 70 to 90 in order to bring it more in
    line with the fraction of the Earth's surface covered with ice, which
    is approximatly .016 (=1.6%). '''

    if (surf_temp > 328.0):
        surf_temp = 328.0
    temp = ((328.0 - surf_temp) / 90.0) ** 5.0
    if temp > (1.5 * hydro_fraction):
        temp = (1.5 * hydro_fraction)
    if temp >= 1.0:
        return 1.0
    else:
        return temp


def eff_temp(ecosphere_radius, orb_radius, albedo):
    '''This is Fogg's eq.19.  The ecosphere radius is given in AU, orbital
    radius in AU, the temperature returned is in Kelvin.'''
    return sqrt(ecosphere_radius / orb_radius) * pow1_4((1.0 - albedo) / (1.0 - EARTH_ALBEDO)) * EARTH_EFFECTIVE_TEMP


def est_temp(ecosphere_radius, orb_radius, albedo):
    return sqrt(ecosphere_radius / orb_radius) * pow1_4((1.0 - albedo) / (1.0 - EARTH_ALBEDO)) * EARTH_AVERAGE_KELVIN


def grnhouse(r_ecosphere, orb_radius):
    '''Old grnhouse:
    Note that if the orbital radius of the planet is greater than or equal
    to R_inner, 99% of it's volatiles are assumed to have been deposited in
    surface reservoirs (otherwise, suffers from the greenhouse effect).

    if ((orb_radius < r_greenhouse) and (zone == 1))

    The definition is based on the inital surface temperature and what
    state water is in. If it's too hot, water will never condense out
    of the atmosphere, down and form an ocean. The albedo used here
    was chosen so that the boundary is about the same as the old method
    Neither zone, r_greenhouse are used in this version        JLB'''

    temp = eff_temp(r_ecosphere, orb_radius, GREENHOUSE_TRIGGER_ALBEDO)

    return temp > FREEZING_POINT_OF_WATER


def green_rise(optical_depth, effective_temp, surf_pressure):
    '''This is Fogg's eq.20, is also Hart's eq.20 in his "Evolution of
    Earth's Atmosphere" article.  The effective temperature given is in
    units of Kelvin, is the rise in temperature produced by the
    greenhouse effect, is returned.
    I tuned this by changing a pow(x,.25) to pow(x,.4) to match Venus - JLB'''
    convection_factor = EARTH_CONVECTION_FACTOR * \
        pow(surf_pressure / EARTH_SURF_PRES_IN_MILLIBARS, 0.4)
    rise = (pow1_4(1.0 + 0.75 * optical_depth) - 1.0) * \
        effective_temp * convection_factor

    if (rise < 0.0):
        rise = 0.0

    return rise


def planet_albedo(water_fraction, cloud_fraction, ice_fraction, surf_pressure):
    '''The surface temperature passed in is in units of Kelvin.
    The cloud adjustment is the fraction of cloud cover obscuring each
    of the three major components of albedo that lie below the clouds.'''

    rock_fraction = 1.0 - water_fraction - ice_fraction
    components = 0.0
    if water_fraction > 0.0:
        components = components + 1.0
    if ice_fraction > 0.0:
        components = components + 1.0
    if rock_fraction > 0.0:
        components = components + 1.0

    cloud_adjustment = cloud_fraction / components

    if rock_fraction >= cloud_adjustment:
        rock_fraction = rock_fraction - cloud_adjustment
    else:
        rock_fraction = 0.0

    if water_fraction > cloud_adjustment:
        water_fraction = water_fraction - cloud_adjustment
    else:
        water_fraction = 0.0

    if ice_fraction > cloud_adjustment:
        ice_fraction = ice_fraction - cloud_adjustment
    else:
        ice_fraction = 0.0

    cloud_part = cloud_fraction * CLOUD_ALBEDO         # about(...,0.2)

    if surf_pressure == 0.0:
        rock_part = rock_fraction * ROCKY_AIRLESS_ALBEDO  # about(...,0.3)
        ice_part = ice_fraction * AIRLESS_ICE_ALBEDO      # about(...,0.4)
        water_part = 0

    else:
        rock_part = rock_fraction * ROCKY_ALBEDO         # about(...,0.1)
        water_part = water_fraction * WATER_ALBEDO       # about(...,0.2)
        ice_part = ice_fraction * ICE_ALBEDO             # about(...,0.1)

    return(cloud_part + rock_part + water_part + ice_part)


def opacity(molecular_weight, surf_pressure):
    '''This function returns the dimensionless quantity of optical depth,
    which is useful in determining the amount of greenhouse effect on a
    planet.'''

    optical_depth = 0.0
    if (molecular_weight >= 0.0) and (molecular_weight < 10.0):
        optical_depth = optical_depth + 3.0
    if (molecular_weight >= 10.0) and (molecular_weight < 20.0):
        optical_depth = optical_depth + 2.34
    if (molecular_weight >= 20.0) and (molecular_weight < 30.0):
        optical_depth = optical_depth + 1.0
    if (molecular_weight >= 30.0) and (molecular_weight < 45.0):
        optical_depth = optical_depth + 0.15
    if (molecular_weight >= 45.0) and (molecular_weight < 100.0):
        optical_depth = optical_depth + 0.05

    if surf_pressure >= (70.0 * EARTH_SURF_PRES_IN_MILLIBARS):
        optical_depth = optical_depth * 8.333
    else:
        if surf_pressure >= (50.0 * EARTH_SURF_PRES_IN_MILLIBARS):
            optical_depth = optical_depth * 6.666
        else:
            if surf_pressure >= (30.0 * EARTH_SURF_PRES_IN_MILLIBARS):
                optical_depth = optical_depth * 3.333
            else:
                if surf_pressure >= (10.0 * EARTH_SURF_PRES_IN_MILLIBARS):
                    optical_depth = optical_depth * 2.0
                else:
                    if surf_pressure >= (5.0 * EARTH_SURF_PRES_IN_MILLIBARS):
                        optical_depth = optical_depth * 1.5

    return(optical_depth)


def gas_life(molecular_weight, planet):
    ''' calculates the number of years it takes for 1/e of a gas to escape  from a planet's atmosphere.
    Taken from Dole p. 34. He cites Jeans (1916) & Jones (1923)'''
    v = rms_vel(molecular_weight, planet.exospheric_temp)
    g = planet.surf_grav * EARTH_ACCELERATION
    r = (planet.radius * CM_PER_KM)
    try:
        t = (pow3(v) / (2.0 * pow2(g) * r)) * exp((3.0 * g * r) / pow2(v))
        years = t / (SECONDS_PER_HOUR * 24.0 * DAYS_IN_A_YEAR)
        if years > 2.0E10:
            years = INCREDIBLY_LARGE_NUMBER
    except OverflowError:
        years = INCREDIBLY_LARGE_NUMBER

    #  long ve = planet.esc_velocity
    #  long k = 2
    #  long t2 = ((k * pow3(v) * r) / pow4(ve)) * exp((3.0 * pow2(ve)) / (2.0 * pow2(v)))
    #  long years2 = t2 / (SECONDS_PER_HOUR * 24.0 * DAYS_IN_A_YEAR)

    #  if VERBOSE:
    #    fprintf (stderr, "gas_life: %LGs, ratio: %Lf\n",
    #        years, ve / v)

    return years


def min_molec_weight(planet):
    '''TODO(woursler): Not sure this is ported well with the guesses and all. Also it's totally unreadable.'''
    mass = planet.mass
    radius = planet.radius
    temp = planet.exospheric_temp
    target = 5.0E9

    guess_1 = molecule_limit(mass, radius, temp)
    guess_2 = guess_1

    life = gas_life(guess_1, planet)

    loops = 0

    if planet.sun:
        target = planet.sun.age
    if life > target:
        while life > target and loops < 25:
            guess_1 = guess_1 / 2.0
            life = gas_life(guess_1, planet)
            loops += 1
    else:
        while life < target and loops < 25:
            guess_2 = guess_2 * 2.0
            life = gas_life(guess_2, planet)
            loops += 1

    loops = 0

    while (guess_2 - guess_1) > 0.1 and loops < 25:
        guess_3 = (guess_1 + guess_2) / 2.0
        life = gas_life(guess_3, planet)

        if life < target:
            guess_1 = guess_3
        else:
            guess_2 = guess_3

        loops += 1

    life = gas_life(guess_2, planet)

    return guess_2


def calculate_surface_temp(planet, first, last_water, last_clouds, last_ice, last_temp, last_albedo):
    '''The temperature calculated is in degrees Kelvin. '''

    boil_off = False

    if first:
        planet.albedo = EARTH_ALBEDO

        effective_temp = eff_temp(
            planet.sun.r_ecosphere, planet.orbit.a, planet.albedo)
        greenhouse_temp = green_rise(opacity(planet.molec_weight,
                                             planet.surf_pressure),
                                     effective_temp,
                                     planet.surf_pressure)
        planet.surf_temp = effective_temp + greenhouse_temp

        set_temp_range(planet)

    if planet.greenhouse_effect and planet.max_temp < planet.boil_point:
        '''if VERBOSE:
            fprintf(stderr, "Deluge: %s %d max (%Lf) < boil (%Lf)\n",
                    planet.sun.name,
                    planet.planet_no,
                    planet.max_temp,
                    planet.boil_point)'''

        planet.greenhouse_effect = 0

        planet.volatile_gas_inventory = vol_inventory(planet.mass,
                                                      planet.esc_velocity,
                                                      planet.rms_velocity,
                                                      planet.sun.mass_ratio,
                                                      planet.orbit_zone,
                                                      planet.greenhouse_effect,
                                                      (planet.gas_mass
                                                       / planet.mass) > 0.000001)
        planet.surf_pressure = pressure(planet.volatile_gas_inventory,
                                        planet.radius,
                                        planet.surf_grav)

        planet.boil_point = boiling_point(planet.surf_pressure)

    water_raw = planet.hydrosphere = hydro_fraction(planet.volatile_gas_inventory,
                                                    planet.radius)
    clouds_raw = planet.cloud_cover = cloud_fraction(planet.surf_temp,
                                                     planet.molec_weight,
                                                     planet.radius,
                                                     planet.hydrosphere)
    planet.ice_cover = ice_fraction(planet.hydrosphere,
                                    planet.surf_temp)

    if planet.greenhouse_effect and (planet.surf_pressure > 0.0):
        planet.cloud_cover = 1.0

    if (planet.high_temp >= planet.boil_point) and (not first) and (not int(planet.day) == int(planet.orb_period * 24.0)) or planet.resonant_period:
        planet.hydrosphere = 0.0
        boil_off = True

        if planet.molec_weight > WATER_VAPOR:
            planet.cloud_cover = 0.0
        else:
            planet.cloud_cover = 1.0

    if planet.surf_temp < (FREEZING_POINT_OF_WATER - 3.0):
        planet.hydrosphere = 0.0

    planet.albedo = planet_albedo(planet.hydrosphere,
                                  planet.cloud_cover,
                                  planet.ice_cover,
                                  planet.surf_pressure)

    effective_temp = eff_temp(planet.sun.r_ecosphere, planet.orbit.a, planet.albedo)
    greenhouse_temp = green_rise(opacity(planet.molec_weight,
                                         planet.surf_pressure),
                                 effective_temp,
                                 planet.surf_pressure)
    planet.surf_temp = effective_temp + greenhouse_temp

    if not first:
        if not boil_off:
            planet.hydrosphere = (planet.hydrosphere + (last_water * 2)) / 3
        planet.cloud_cover = (planet.cloud_cover + (last_clouds * 2)) / 3
        planet.ice_cover = (planet.ice_cover + (last_ice * 2)) / 3
        planet.albedo = (planet.albedo + (last_albedo * 2)) / 3
        planet.surf_temp = (planet.surf_temp + (last_temp * 2)) / 3

    set_temp_range(planet)

    if VERBOSE:
        print("calculate_surface_temp readout\n" + tabulate([
            ["AU", planet.orbit.a],
            ["Surface Temp C", planet.surf_temp - FREEZING_POINT_OF_WATER],
            ["Effective Temp C", effective_temp - FREEZING_POINT_OF_WATER],
            ["Greenhouse Temp", greenhouse_temp],
            ["Water Cover", planet.hydrosphere],
            ["water_raw", water_raw],
            ["Cloud Cover", planet.cloud_cover],
            ["clouds_raw", clouds_raw],
            ["Ice Cover", planet.ice_cover],
            ["Albedo", planet.albedo],
        ]))


def iterate_surface_temp(planet):
    initial_temp = est_temp(planet.sun.r_ecosphere, planet.orbit.a, planet.albedo)

    if VERBOSE:
        print(tabulate([
            ["Initial temp", initial_temp],
            ["Solar Ecosphere", planet.sun.r_ecosphere],
            ["AU", planet.orbit.a],
            ["Albedo", planet.albedo],
        ]))

        h2_life = gas_life(MOL_HYDROGEN,    planet)
        h2o_life = gas_life(WATER_VAPOR,     planet)
        n2_life = gas_life(MOL_NITROGEN,    planet)
        n_life = gas_life(ATOMIC_NITROGEN, planet)

        print('Gas lifetimes:\n' + tabulate([
            ['H2', h2_life],
            ['H2O', h2o_life],
            ['N', n_life],
            ['N2', n2_life],
        ]))

    calculate_surface_temp(planet, True, 0, 0, 0, 0, 0)

    for _ in range(26):  # TODO(woursler): WTF is this magic number? just an iteration limit? Should be a param.
        last_water = planet.hydrosphere
        last_clouds = planet.cloud_cover
        last_ice = planet.ice_cover
        last_temp = planet.surf_temp
        last_albedo = planet.albedo

        calculate_surface_temp(planet, False,
                               last_water, last_clouds, last_ice,
                               last_temp, last_albedo)

        if fabs(planet.surf_temp - last_temp) < 0.25:
            break

    planet.greenhs_rise = planet.surf_temp - initial_temp

    '''
    if VERBOSE:
        fprintf(stderr, "%d: %5.gh = %5.1Lf (%5.1Lf C) st - %5.1Lf it [%5.1Lf re %5.1Lf a %5.1Lf alb]\n",
                planet.planet_no,
                planet.greenhs_rise,
                planet.surf_temp,
                planet.surf_temp - FREEZING_POINT_OF_WATER,
                initial_temp,
                planet.sun.r_ecosphere, planet.a, planet.albedo
                )
'''


# TODO(woursler): Move this into an atomosphere class.

def inspired_partial_pressure(surf_pressure, gas_pressure):
    '''Inspired partial pressure, takes into account humidification of the
    air in the nasal passage and throat This formula is on Dole's p. 14'''
    pH2O = H20_ASSUMED_PRESSURE
    fraction = gas_pressure / surf_pressure

    return (surf_pressure - pH2O) * fraction


def breathability(planet):
    '''This function uses figures on the maximum inspired partial pressures
    of Oxygen, atmospheric and traces gases as laid out on pages 15,
    16 and 18 of Dole's Habitable Planets for Man to derive breathability
    of the planet's atmosphere.                                       JLB'''
    oxygen_ok = False

    if planet.gases == 0:
        return BreathabilityPhrase.NONE

    for index in range(planet.gases):
        gas_no = 0

        ipp = inspired_partial_pressure(planet.surf_pressure,
                                        planet.atmosphere[index].surf_pressure)

        for n in range(len(planet.gases)):
            if planet.gases[n].num == planet.atmosphere[index].num:
                gas_no = n

        if ipp > planet.gases[gas_no].max_ipp:
            return BreathabilityPhrase.POISONOUS

        if planet.atmosphere[index].num == AN_O:
            oxygen_ok = ((ipp >= MIN_O2_IPP) and (ipp <= MAX_O2_IPP))

    if oxygen_ok:
        return BreathabilityPhrase.BREATHABLE
    else:
        return BreathabilityPhrase.UNBREATHABLE


def lim(x):
    '''function for 'soft limiting' temperatures'''
    return x / sqrt(sqrt(1 + x**4))


def soft(v, max, min):
    dv = v - min
    dm = max - min
    return (lim(2*dv/dm-1)+1)/2 * dm + min


def set_temp_range(planet):
    pressmod = 1 / sqrt(1 + 20 * planet.surf_pressure/1000.0)
    ppmod = 1 / sqrt(10 + 5 * planet.surf_pressure/1000.0)
    tiltmod = fabs(cos(planet.axial_tilt * pi/180) * pow(1 + planet.orbit.e, 2))
    daymod = 1 / (200/planet.day + 1)
    mh = pow(1 + daymod, pressmod)
    ml = pow(1 - daymod, pressmod)
    hi = mh * planet.surf_temp
    lo = ml * planet.surf_temp
    sh = hi + pow((100+hi) * tiltmod, sqrt(ppmod))
    wl = lo - pow((150+lo) * tiltmod, sqrt(ppmod))
    max = planet.surf_temp + sqrt(planet.surf_temp) * 10
    min = planet.surf_temp / sqrt(planet.day + 24)

    if lo < min:
        lo = min
    if wl < 0:
        wl = 0

    planet.high_temp = soft(hi, max, min)
    planet.low_temp = soft(lo, max, min)
    planet.max_temp = soft(sh, max, min)
    planet.min_temp = soft(wl, max, min)
