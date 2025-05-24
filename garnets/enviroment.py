from enum import Enum
from math import exp
from math import inf as INCREDIBLY_LARGE_NUMBER
from math import log
from math import pi

from attr import attr
from attr import attrs
from chemtable import lookup_gas
from constants import AIRLESS_ICE_ALBEDO
from constants import CHANGE_IN_EARTH_ANG_VEL
from constants import CLOUD_ALBEDO
from constants import CLOUD_COVERAGE_FACTOR
from constants import EARTH_ALBEDO
from constants import EARTH_AVERAGE_TEMP
from constants import EARTH_AXIAL_TILT
from constants import EARTH_CONVECTION_FACTOR
from constants import EARTH_DENSITY
from constants import EARTH_EFFECTIVE_TEMP
from constants import EARTH_RADIUS
from constants import EARTH_WATER_MASS_PER_AREA
from constants import FREEZING_POINT_OF_WATER
from constants import GAS_RETENTION_THRESHOLD
from constants import GRAV_CONSTANT
from constants import GREENHOUSE_TRIGGER_ALBEDO
from constants import H2O_ASSUMED_PRESSURE
from constants import ICE_ALBEDO
from constants import J
from constants import MOLAR_GAS_CONST
from constants import ROCKY_AIRLESS_ALBEDO
from constants import ROCKY_ALBEDO
from constants import WATER_ALBEDO
from tabulate import tabulate
from xatu.core import dimensionless_with_units
from xatu.core import quantity_repr
from xatu.core import with_units
from xatu.math import cos
from xatu.math import sqrt
from xatu.units import K
from xatu.units import atm
from xatu.units import au
from xatu.units import bar
from xatu.units import cm
from xatu.units import deg
from xatu.units import earth_mass
from xatu.units import gee
from xatu.units import gram
from xatu.units import hour
from xatu.units import kg
from xatu.units import km
from xatu.units import m
from xatu.units import mol
from xatu.units import rad
from xatu.units import s
from xatu.units import solar_mass
from xatu.units import turn
from xatu.units import year

# TODO(woursler): Break this file up.

VERBOSE = True


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
    ASTERIODS = 10
    # TODO(woursler): Don't know what this means... maybe tidally locked?
    TIDALLY_LOCKED = 11


class Zone(Enum):
    # TODO(woursler): Figure out the meaning of this?
    # Might be related to habitable zone?
    # Given in Fogg 85. Seems to be a ... very simplified solar system model.
    ZONE_1 = 1
    ZONE_2 = 2
    ZONE_3 = 3


def orb_zone(luminosity, orb_radius):
    '''The orbital 'zone' of the particle.'''
    if orb_radius < (4 * sqrt(luminosity) * au):
        return Zone.ZONE_1
    elif orb_radius < (15 * sqrt(luminosity) * au):
        return Zone.ZONE_2
    else:
        return Zone.ZONE_3


def volume_radius(mass, density):
    volume = mass / density
    return (volume / ((4/3) * pi))**(1/3)


def kothari_radius(mass, giant, zone):
    '''Returns the radius of the planet in kilometers.

    See "The Internal Constitution of Planets", by
    Dr. D. S. Kothari, Mon. Not. of the Royal Astronomical Society, 96
    pp.833-843, for the derivation. Page 840 has all the equations used here.

    Common atomic_weights / atomic_nums are likely taken from Fogg?
    '''

    # TODO(woursler): Move this outside, so that more specific materials
    # may be given.
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

    # See documentation: //docs/kothari.md
    # Kothari eq. 25
    radius_maximizing_mass = 1.04 * 10 ** -3 * \
        (atomic_num ** 3 / atomic_weight ** 2) * solar_mass
    # Kothari eq. 26
    maximum_radius = 1.12 * 10 ** 10 * \
        (atomic_num ** (2/3) / atomic_num) * cm

    # Kothari eq. 26'
    mass_ratio = mass / radius_maximizing_mass
    return maximum_radius * 2 * mass_ratio ** (1/3) / (1 + mass_ratio ** (2/3))


def empirical_density(mass, orb_radius, r_ecosphere, gas_giant):

    # TODO(woursler): WTF is this? Re work some way that makes a lick of sense.

    mass = dimensionless_with_units(mass, earth_mass)
    orb_radius = dimensionless_with_units(orb_radius, au)
    r_ecosphere = dimensionless_with_units(r_ecosphere, au)

    temp = (sqrt(mass) * r_ecosphere / orb_radius)**(1/4) * gram / cm ** 3
    if gas_giant:
        return (temp * 1.2)
    else:
        return (temp * 5.5)


def volume_density(mass, equat_radius):
    volume = (4 / 3) * pi * equat_radius**3
    return (mass / volume)


def period(separation, small_mass, large_mass):
    '''The total period of the given two-body co-orbital system.'''
    if small_mass > large_mass:
        return period(separation, large_mass, small_mass)

    if separation == 0 * km:
        return 0 * year

    if large_mass == 0 * kg:
        return inf * year

    if small_mass == 0 * kg:
        return 2 * pi * sqrt(separation**3 / large_mass / GRAV_CONSTANT)

    reduced_mass = with_units(
        (small_mass * large_mass) / (small_mass + large_mass),
        kg,
    )

    return 2 * pi * sqrt(separation**3 / reduced_mass / GRAV_CONSTANT)


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

    year_length = with_units(planet.orb_period, year)
    giant = (planet.type == PlanetType.GAS_GIANT
             or planet.type == PlanetType.SUB_GAS_GIANT
             or planet.type == PlanetType.SUB_SUB_GAS_GIANT)

    stopped = False

    planet.resonant_period = False  # Warning: Modifies the planet

    if giant:
        k2 = 0.24
    else:
        k2 = 0.33

    base_angular_velocity = with_units(
        sqrt(2.0 * J * (planet.mass) / (k2 * (planet.radius**2))) * rad,
        rad / s,
    )

    # This next calculation determines how much the planet's rotation is
    # slowed by the presence of the star.

    # TODO(woursler): Replace with an actual tidal force calculation,
    # including love numbers and such.
    change_in_angular_velocity = CHANGE_IN_EARTH_ANG_VEL \
        * (planet.density / EARTH_DENSITY) \
        * (planet.radius / EARTH_RADIUS) \
        * (earth_mass / planet.mass) \
        * (planet.sun.mass_ratio ** 2) \
        * (au ** 6 / (planet.orbit.a ** 6))

    ang_velocity = base_angular_velocity + \
        (change_in_angular_velocity * planet.sun.age)

    if ang_velocity <= 0 * rad / s:
        stopped = True
        day_length = INCREDIBLY_LARGE_NUMBER * hour

    else:
        day_length = with_units(
            turn / ang_velocity,
            hour
        )

    if (day_length >= year_length) or stopped:
        # TODO(woursler): Determine what phenomenon this models.
        if planet.orbit.e > 0.1:
            spin_resonance_factor = (1.0 - planet.orbit.e) / (1.0 +
                                                              planet.orbit.e)
            planet.resonant_period = True
            return (spin_resonance_factor * year_length)

        else:
            return year_length

    return day_length


def inclination(orb_radius):
    '''The orbital radius is expected in units of Astronomical Units (AU).
    Inclination is returned in units of degrees. '''
    temp = int((orb_radius**0.2) *
               random.uniform(EARTH_AXIAL_TILT - 0.4, EARTH_AXIAL_TILT + 0.4))
    return (temp % 360) * deg


def escape_vel(mass, radius):
    '''This function implements the escape velocity calculation.  Note that
    it appears that Fogg's eq.15 is incorrect.
    TODO(woursler): WTF? How is something this basic in dispute? Why does the radius matter?'''
    return sqrt(2 * GRAV_CONSTANT * mass / radius)


def rms_vel(molecular_weight, exospheric_temp):
    '''This is Fogg's eq.16.  The molecular weight (usually assumed to be N2)
    is used as the basis of the Root Mean Square (RMS) velocity of the
    molecule or atom. '''

    molecular_weight = with_units(molecular_weight, gram/mol)
    exospheric_temp = with_units(exospheric_temp, K)
    v = sqrt(
        3 * MOLAR_GAS_CONST * exospheric_temp / molecular_weight,
    )
    return with_units(v, m/s)


def molecule_limit(mass, equat_radius, exospheric_temp):
    '''This function returns the smallest molecular weight retained by the
    body, is useful for determining the atmosphere composition.
    Mass is in units of solar masses, equatorial radius is in units of
    kilometers. '''
    esc_velocity = escape_vel(mass, equat_radius)

    return (3 * MOLAR_GAS_CONST * exospheric_temp) \
        / (esc_velocity / GAS_RETENTION_THRESHOLD) ** 2


def acceleration(mass, radius):
    '''This function calculates the surface acceleration of a planet.'''

    return GRAV_CONSTANT * mass / radius ** 2


def vol_inventory(mass, escape_vel, rms_vel, stellar_mass, zone,
                  greenhouse_effect, accreted_gas):
    '''This implements Fogg's eq.17.  The 'inventory' returned is unitless.

    There is, best I can tell, an extremely poor justification for this number.'''

    velocity_ratio = escape_vel / rms_vel
    if velocity_ratio >= GAS_RETENTION_THRESHOLD:
        if zone == Zone.ZONE_1:
            proportion_ = 140000.0
            '''100 . 140 JLB'''
            #  10000 in Fogg 85
        elif zone == Zone.ZONE_2:
            proportion_ = 75000.0
        elif zone == Zone.ZONE_3:
            proportion_ = 250.0
        else:
            raise NotImplementedError("orbital zone not initialized correctly")

        earth_units = dimensionless_with_units(mass, earth_mass)
        temp2 = (proportion_ * earth_units) / stellar_mass

        if greenhouse_effect or accreted_gas:
            return temp2
        else:
            return temp2 / 140.0  # 100 . 140 JLB

    else:
        return 0.0


def pressure(volatile_gas_inventory, equat_radius, gravity):
    '''This implements Fogg's eq.18.'''

    radius_ratio = equat_radius / EARTH_RADIUS
    gravity_ratio = dimensionless_with_units(gravity, gee)

    vgi_earth = 10000  # Taken from Fogg 85.
    vgi_ratio = volatile_gas_inventory / vgi_earth

    return atm * vgi_ratio \
        * gravity_ratio \
        / (radius_ratio**2)


def boiling_point(surf_pressure):
    '''This function returns the boiling point of water in an atmosphere of
    pressure 'surf_pressure', in millibars.  The boiling point is
    returned in units of Kelvin.  This is Fogg's eq.21.

    # TODO(woursler): This would be better as part of a phase diagram.
    '''

    return 1.0 / (
        (
            log(dimensionless_with_units(surf_pressure, bar))
            / -5050.5
        ) + (1.0 / 373.0)
    ) * K


def hydro_fraction(volatile_gas_inventory, planet_radius):
    '''This function is Fogg's eq.22.   Given the volatile gas inventory and
    planetary radius of a planet (in Km), function returns the
    fraction of the planet covered with water.
    I have changed the function very slightly:   the fraction of Earth's
    surface covered by water is 71%, not 75% as Fogg used. '''

    temp = (0.71 * volatile_gas_inventory / 1000.0) * \
        ((EARTH_RADIUS / planet_radius) ** 2)
    if temp >= 1.0:
        return 1.0
    else:
        return temp


# Constant only used here and not really explained.
Q2_36 = 0.0698 / K


def cloud_fraction(surf_temp, smallest_MW_retained, equat_radius,
                   hydro_fraction):
    '''Given the surface temperature of a planet (in Kelvin), function
    returns the fraction of cloud cover available.   This is Fogg's eq.23.
    See Hart in "Icarus" (vol 33, pp23 - 39, 1978) for an explanation.
    This equation is Hart's eq.3.
    I have modified it slightly using constants and relationships from
    Glass's book "Introduction to Planetary Geology", p.46.
    The 'CLOUD_COVERAGE_FACTOR' is the amount of surface area on Earth
    covered by one Kg. of cloud.'''

    surf_temp = dimensionless_with_units(surf_temp, K)

    if smallest_MW_retained > lookup_gas('H2O').weight:
        return 0.0
    else:
        surf_area = 4.0 * pi * (equat_radius**2)
        hydro_mass = hydro_fraction * surf_area * EARTH_WATER_MASS_PER_AREA
        water_vapor_in_kg = (0.00000001 * hydro_mass) * \
            exp(Q2_36 * (surf_temp * K - EARTH_AVERAGE_TEMP))
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

    surf_temp = dimensionless_with_units(surf_temp, K)

    if (surf_temp > 328.0):
        surf_temp = 328.0
    temp = ((328.0 - surf_temp) / 90.0)**5.0
    if temp > (1.5 * hydro_fraction):
        temp = (1.5 * hydro_fraction)
    if temp >= 1.0:
        return 1.0
    else:
        return temp


def eff_temp(ecosphere_radius, orb_radius, albedo):
    '''This is Fogg's eq.19.  The ecosphere radius is given in AU, orbital
    radius in AU, the temperature returned is in Kelvin.'''
    return EARTH_EFFECTIVE_TEMP * sqrt(ecosphere_radius / orb_radius) * (
        (1.0 - albedo) / (1.0 - EARTH_ALBEDO)) ** (1/4)


def est_temp(ecosphere_radius, orb_radius, albedo):
    return EARTH_AVERAGE_TEMP * sqrt(ecosphere_radius / orb_radius) * (
        (1.0 - albedo) / (1.0 - EARTH_ALBEDO)) ** (1/4)


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
    # TODO(woursler): Undo whatever JLB did.
    I tuned this by changing a pow(x,.25) to pow(x,.4) to match Venus - JLB'''
    convection_factor = EARTH_CONVECTION_FACTOR * \
        pow(dimensionless_with_units(surf_pressure, atm), 0.4)
    rise = ((1.0 + 0.75 * optical_depth) ** (1/4) - 1.0) * \
        effective_temp * convection_factor

    if rise < 0 * K:
        rise = 0 * K

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

    cloud_part = cloud_fraction * CLOUD_ALBEDO  # about(...,0.2)

    if surf_pressure == 0 * atm:
        rock_part = rock_fraction * ROCKY_AIRLESS_ALBEDO  # about(...,0.3)
        ice_part = ice_fraction * AIRLESS_ICE_ALBEDO  # about(...,0.4)
        water_part = 0

    else:
        rock_part = rock_fraction * ROCKY_ALBEDO  # about(...,0.1)
        water_part = water_fraction * WATER_ALBEDO  # about(...,0.2)
        ice_part = ice_fraction * ICE_ALBEDO  # about(...,0.1)

    return (cloud_part + rock_part + water_part + ice_part)


def opacity(molecular_weight, surf_pressure):
    '''This function returns the dimensionless quantity of optical depth,
    which is useful in determining the amount of greenhouse effect on a
    planet.'''

    optical_depth = 0.0
    if (molecular_weight >= 0 * kg/mol) and (molecular_weight < 10 * kg/mol):
        optical_depth = optical_depth + 3.0
    if (molecular_weight >= 10 * kg/mol) and (molecular_weight < 20 * kg/mol):
        optical_depth = optical_depth + 2.34
    if (molecular_weight >= 20 * kg/mol) and (molecular_weight < 30 * kg/mol):
        optical_depth = optical_depth + 1.0
    if (molecular_weight >= 30 * kg/mol) and (molecular_weight < 45 * kg/mol):
        optical_depth = optical_depth + 0.15
    if (molecular_weight >= 45 * kg/mol) and (molecular_weight < 100 * kg/mol):
        optical_depth = optical_depth + 0.05

    if surf_pressure >= 70 * atm:
        optical_depth = optical_depth * 8.333
    elif surf_pressure >= 50 * atm:
        optical_depth = optical_depth * 6.666
    elif surf_pressure >= 30 * atm:
        optical_depth = optical_depth * 3.333
    elif surf_pressure >= 10 * atm:
        optical_depth = optical_depth * 2.0
    elif surf_pressure >= 5 * atm:
        optical_depth = optical_depth * 1.5

    return (optical_depth)


def gas_life(gas, planet):
    '''Calculates the number of years it takes for 1/e of a gas to escape  from a planet's atmosphere.
    Taken from Dole p. 34. He cites Jeans (1916) & Jones (1923)

    # TODO(woursler): Properly implement Jeans Escape...
    https://en.wikipedia.org/wiki/Atmospheric_escape
    '''
    molecular_weight = gas.weight
    # TODO(woursler): v_0 != v_rms
    v = rms_vel(molecular_weight, planet.exospheric_temp)

    try:
        t = v ** 3 / (2 * planet.radius * planet.surf_grav ** 2) * \
            exp(3 * planet.radius * planet.surf_grav / v ** 2)
        if t > 2.0E10 * year:
            return INCREDIBLY_LARGE_NUMBER * year
        return t
    except OverflowError:
        return INCREDIBLY_LARGE_NUMBER * year


@attrs
class GasWrapper:
    weight = attr()


def min_molec_weight(planet):
    '''Determines the smallest molecular weight expected to be retained in
    significant quantities.

    While a fixed solution is possible

    TODO(woursler): Not sure this is ported well with the guesses and all.
    Also it's totally unreadable.

    # DO NOT COMMIT(woursler): Implement.
    '''

    mass = planet.mass
    radius = planet.radius
    temp = planet.exospheric_temp

    if planet.sun:
        target = planet.sun.age
    else:
        target = 5.0E9 * year

    lower_bound = lookup_gas('H').weight

    # This upper bound may be too small,
    # but is sufficiently large for most earthlike planets.
    upper_bound = lookup_gas('N2').weight

    # If the planet can retain free hydrogen, it can retain any gas.
    if gas_life(GasWrapper(weight=lower_bound), planet) < target:
        return lower_bound

    # Ensure that upper_bound > mmw while keeping lower_bound < mmw
    while gas_life(GasWrapper(weight=upper_bound), planet) < target:
        lower_bound = upper_bound
        upper_bound = 2 * upper_bound

    # Binary search for the threshold where gas_life(...) == target
    loops = 0
    while loops < 25:
        loops += 1
        midpoint = (lower_bound + upper_bound) / 2

        if upper_bound <= lower_bound:
            break

        if gas_life(GasWrapper(weight=midpoint), planet) < target:
            lower_bound = midpoint
        else:
            upper_bound = midpoint

    return midpoint


def calculate_surface_temp(planet, first, last_water, last_clouds, last_ice,
                           last_temp, last_albedo):
    '''The temperature calculated is in degrees Kelvin. '''

    boil_off = False

    if first:
        planet.albedo = EARTH_ALBEDO

        effective_temp = eff_temp(planet.sun.r_ecosphere, planet.orbit.a,
                                  planet.albedo)
        greenhouse_temp = green_rise(
            opacity(planet.molec_weight, planet.surf_pressure), effective_temp,
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

        planet.volatile_gas_inventory = vol_inventory(
            planet.mass, planet.esc_velocity, planet.rms_velocity,
            planet.sun.mass_ratio, planet.orbit_zone, planet.greenhouse_effect,
            (planet.gas_mass / planet.mass) > 0.000001)
        planet.surf_pressure = pressure(planet.volatile_gas_inventory,
                                        planet.radius, planet.surf_grav)

        planet.boil_point = boiling_point(planet.surf_pressure)

    water_raw = planet.hydrosphere = hydro_fraction(
        planet.volatile_gas_inventory, planet.radius)
    clouds_raw = planet.cloud_cover = cloud_fraction(planet.surf_temp,
                                                     planet.molec_weight,
                                                     planet.radius,
                                                     planet.hydrosphere)
    planet.ice_cover = ice_fraction(planet.hydrosphere, planet.surf_temp)

    if planet.greenhouse_effect and (planet.surf_pressure > 0 * atm):
        planet.cloud_cover = 1.0

    if (planet.high_temp >= planet.boil_point) \
            and (not first) \
            and (
                int(dimensionless_with_units(planet.day, hour))
                != int(dimensionless_with_units(planet.orb_period, hour))) \
            or planet.resonant_period:
        planet.hydrosphere = 0.0
        boil_off = True

        if planet.molec_weight > lookup_gas('H2O').weight:
            planet.cloud_cover = 0.0
        else:
            planet.cloud_cover = 1.0

    if planet.surf_temp + 3*K < FREEZING_POINT_OF_WATER:
        planet.hydrosphere = 0.0

    planet.albedo = planet_albedo(planet.hydrosphere, planet.cloud_cover,
                                  planet.ice_cover, planet.surf_pressure)

    effective_temp = eff_temp(planet.sun.r_ecosphere, planet.orbit.a,
                              planet.albedo)
    greenhouse_temp = green_rise(
        opacity(planet.molec_weight, planet.surf_pressure), effective_temp,
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
            ["Orbital Radius", quantity_repr(planet.orbit.a, au)],
            ["Surface Temp", quantity_repr(planet.surf_temp, K)],
            ["Effective Temp", quantity_repr(effective_temp, K)],
            ["Greenhouse Temp", quantity_repr(greenhouse_temp, K)],
            ["Water Cover", planet.hydrosphere],
            ["water_raw", water_raw],
            ["Cloud Cover", planet.cloud_cover],
            ["clouds_raw", clouds_raw],
            ["Ice Cover", planet.ice_cover],
            ["Albedo", planet.albedo],
        ]))


def iterate_surface_temp(planet):
    initial_temp = est_temp(
        planet.sun.r_ecosphere,
        planet.orbit.a,
        planet.albedo,
    )

    if VERBOSE:
        print(
            tabulate([
                ["Initial temp", quantity_repr(initial_temp, K)],
                ["Solar Ecosphere", quantity_repr(planet.sun.r_ecosphere, au)],
                ["Orbital Radius", quantity_repr(planet.orbit.a, au)],
                ["Albedo", planet.albedo],
            ]))

        h2_life = gas_life(lookup_gas('H2'), planet)
        h2o_life = gas_life(lookup_gas('H2O'), planet)
        n2_life = gas_life(lookup_gas('N2'), planet)
        n_life = gas_life(lookup_gas('N'), planet)

        print('Gas lifetimes:\n' + tabulate([
            ['H2', quantity_repr(h2_life, year)],
            ['H2O', quantity_repr(h2o_life, year)],
            ['N', quantity_repr(n_life, year)],
            ['N2', quantity_repr(n2_life, year)],
        ]))

    calculate_surface_temp(planet, True, 0, 0, 0, 0, 0)

    # TODO(woursler): WTF is this magic number? just an iteration limit? Should be a param.
    for _ in range(26):
        last_water = planet.hydrosphere
        last_clouds = planet.cloud_cover
        last_ice = planet.ice_cover
        last_temp = planet.surf_temp
        last_albedo = planet.albedo

        calculate_surface_temp(planet, False, last_water, last_clouds,
                               last_ice, last_temp, last_albedo)

        if abs(planet.surf_temp - last_temp) < 0.25 * K:
            break

    planet.greenhs_rise = planet.surf_temp - initial_temp

    if VERBOSE:
        print("iterate_surface_temp readout\n" + tabulate([
            ["greenhs_rise", quantity_repr(planet.greenhs_rise, K)],
            ["surf_temp", quantity_repr(planet.surf_temp, K)],
            ["surf_temp - FREEZING_POINT_OF_WATER",
             quantity_repr(planet.surf_temp - FREEZING_POINT_OF_WATER, K)],
            ["Initial temp", quantity_repr(initial_temp, K)],
            ["Solar Ecosphere", quantity_repr(planet.sun.r_ecosphere, au)],
            ["Orbital Radius", quantity_repr(planet.orbit.a, au)],
            ["Albedo", planet.albedo],
        ]))


# TODO(woursler): Move this into an atomosphere class.


def inspired_partial_pressure(surf_pressure, gas_pressure):
    '''Inspired partial pressure, takes into account humidification of the
    air in the nasal passage and throat This formula is on Dole's p. 14'''
    pH2O = H2O_ASSUMED_PRESSURE
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
    return (lim(2 * dv / dm - 1) + 1) / 2 * dm + min


def set_temp_range(planet):
    surf_press = dimensionless_with_units(planet.surf_pressure, bar)
    surf_temp = dimensionless_with_units(planet.surf_temp, K)
    day_len = dimensionless_with_units(planet.day, hour)

    pressmod = 1 / sqrt(
        1 + 20 * surf_press
    )
    ppmod = 1 / sqrt(
        10 + 5 * surf_press
    )

    tiltmod = abs(
        cos(planet.axial_tilt) * (1 + planet.orbit.e) ** 2)
    daymod = 1 / (200 / day_len + 1)
    mh = pow(1 + daymod, pressmod)
    ml = pow(1 - daymod, pressmod)
    hi = mh * surf_temp
    lo = ml * surf_temp
    sh = hi + pow((100 + hi) * tiltmod, sqrt(ppmod))
    wl = lo - pow((150 + lo) * tiltmod, sqrt(ppmod))
    max = surf_temp + sqrt(surf_temp) * 10
    min = surf_temp / \
        sqrt(day_len + 24)

    if lo < min:
        lo = min
    if wl < 0:
        wl = 0

    planet.high_temp = soft(hi, max, min) * K
    planet.low_temp = soft(lo, max, min) * K
    planet.max_temp = soft(sh, max, min) * K
    planet.min_temp = soft(wl, max, min) * K
