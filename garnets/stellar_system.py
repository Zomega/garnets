from math import sqrt
from tabulate import tabulate

from attr import attr
from attr import attrs
from constants import B
from constants import DISK_ECCENTRICITY
from enviroment import PlanetType
from xatu.core import dimensionless_with_units
from xatu.core import quantity_formatter
from xatu.core import quantity_repr
from xatu.units import K
from xatu.units import atm
from xatu.units import au
from xatu.units import deg
from xatu.units import earth_mass
from xatu.units import g_force
from xatu.units import jupiter_mass
from xatu.units import kg
from xatu.units import km
from xatu.units import lunar_mass
from xatu.units import neptune_mass
from xatu.units import solar_mass
from xatu.units import year

# pylint: disable=no-member, too-few-public-methods

@attrs(repr=False)
class Star():
    mass_ratio = attr()
    age = attr()

    name = attr(default="Unnamed Star")

    planets = attr(factory=list)

    @property
    def mass(self):
        return self.mass_ratio * solar_mass
    

    @property
    # Approximates the luminosity of the star.
    # TODO: express only as ratio?
    # Source: http://en.wikipedia.org/wiki/Mass%E2%80%93luminosity_relation
    def luminosity_ratio(self):
        if (self.mass_ratio < .43):
            return .23 * (self.mass_ratio**2.3)
        if (self.mass_ratio < 2):
            return (self.mass_ratio**4)
        # Main Sequence Stars
        if (self.mass_ratio < 20):
            return 1.5 * (self.mass_ratio**3.5)
        # For HUGE stars...
        return 3200 * self.mass_ratio

    @property
    # Source: StarGen, TODO Verify against current data.
    def stellar_dust_limit(self):
        return 200 * (self.mass_ratio**(1/3)) * au

    @property
    def r_ecosphere(self):  # Source: StarGen, TODO Name? Value? Possible habitable zone?
        return sqrt(self.luminosity_ratio) * au

    @property
    def min_r_ecosphere(self):
        return sqrt(self.luminosity_ratio / 1.51) * au

    @property
    def max_r_ecosphere(self):
        return sqrt(self.luminosity_ratio / 0.48) * au

    @property
    def life(self):  # Source: StarGen, TODO Name? Value?
        return 10**10 * (self.mass_ratio / self.luminosity_ratio)

    @property
    def innermost_planet(self):
        return min(self.planets, key=lambda p: p.orbit.a)

    @property
    def outermost_planet(self):
        return max(self.planets, key=lambda p: p.orbit.a)
    
    

    def __repr__(self):
        return self.name + ": mass = " + mass_repr(
            self.mass) + "; age = " + quantity_repr(
                self.age, year) + '\n' + '\n'.join(
                    [repr(planet) for planet in self.planets])


@attrs
class StellarSystem:
    star = attr()
    planets = attr()


@attrs
class Orbit:
    a = attr(repr=quantity_formatter(au))  # semi-major axis of solar orbit
    e = attr()  # eccentricity of solar orbit

    @property
    def periapsis(self):
        return (1 - self.e) * self.a

    @property
    def apoapsis(self):
        return (1 + self.e) * self.a


STAR_MASS = 1 * solar_mass  # TODO(woursler): Use the actual star mass


@attrs
class Planetoid():
    orbit = attr()
    dust_mass = attr(repr=quantity_formatter(kg))
    gas_mass = attr(repr=quantity_formatter(kg))

    @property
    def mass(self):
        return self.dust_mass + self.gas_mass

    @property
    def reduced_mass(self):
        # To understand what this is all about...
        # http://spiff.rit.edu/classes/phys440/lectures/reduced/reduced.html
        # But some sort of 3 body case, see dole.
        # TODO: Understand better?
        # TODO(woursler): Actually use the mass of the star?
        return (self.mass / (STAR_MASS + self.mass))**0.25

    @property
    def inner_effect_limit(self):
        # TODO(woursler): Should extend further in, include dust destabilized
        # by indirect gravitational effects.
        return self.orbit.a * (1.0 - self.orbit.e) / (1.0 + DISK_ECCENTRICITY)

    @property
    def outer_effect_limit(self):
        # TODO(woursler): See note on inner_effect_limit
        return self.orbit.a * (1.0 + self.orbit.e) / (1.0 - DISK_ECCENTRICITY)


@attrs
class Planetesimal(Planetoid):
    disk = attr()

    @property
    def critical_mass(self):
        perihelion_dist = self.orbit.a * (1 - self.orbit.e)
        temp = perihelion_dist * sqrt(self.disk.star.luminosity_ratio)
        # TODO(woursler): Understand the basis for this.
        return B * (dimensionless_with_units(temp, au)**-0.75) * solar_mass


# TODO(woursler): Migrate to xatu core...
# quantity_repr(mass, {lunar_mass, earth_mass, jupiter_mass, solar_mass})
# or even quantity_repr(mass, celestial_mass_units)
def mass_repr(mass) -> str:
    if mass <= 50 * lunar_mass:
        return quantity_repr(mass, lunar_mass, ndigits = 2)
    if mass <= 50 * earth_mass:
        return quantity_repr(mass, earth_mass, ndigits = 2)
    if mass <= 15 * neptune_mass:
        return quantity_repr(mass, neptune_mass, ndigits = 2)
    if mass <= 50 * jupiter_mass:
        return quantity_repr(mass, jupiter_mass, ndigits = 2)
    return quantity_repr(mass, solar_mass)


@attrs(repr=False)
class Protoplanet(Planetoid):
    star = attr()
    moons = attr(factory=list)

    def add_moon(self, moon):
        self.moons.append(moon)

    @property
    def mass_of_moons(self):
        if len(self.moons) == 0:
            return 0 * kg
        return sum([moon.mass for moon in self.moons])

    @property
    def critical_mass(self):
        perihelion_dist = self.orbit.a * (1 - self.orbit.e)
        temp = perihelion_dist * sqrt(self.star.luminosity_ratio)
        return B * (dimensionless_with_units(temp, au)**-0.75) * solar_mass

    def __repr__(self):
        return ("\tMass: " + mass_repr(self.mass) + " Orbit: " +
                quantity_repr(self.orbit.a, au) + " AU, Moons: " + str(len(self.moons)) +
                "\n")


@attrs
class Protomoon(Planetoid):
    protoplanet = attr()


# TODO(woursler): Go over these with a fine tooth comb. Many are not relevant, or only relevant during initialization.
# Many should be properties.
# Many should be initialized differently.
@attrs(repr=False)
class Planet():
    # Orbital details.
    orbit = attr()

    axial_tilt = attr(repr=quantity_formatter(deg))  # units of degrees
    mass = attr(repr=quantity_formatter(kg))  # mass (in solar masses)
    dust_mass = attr(repr=quantity_formatter(kg))  # mass, ignoring gas
    gas_mass = attr(repr=quantity_formatter(kg))  # mass, ignoring dust

    moons = attr(factory=list)

    #   ZEROES start here -- TODO(woursler): A bunch of these should be other Zero-like types.
    gas_giant = attr(default=False)  # TRUE if the planet is a gas giant
    # semi-major axis of lunar orbit
    moon_a = attr(factory=lambda: 0*au, repr=quantity_formatter(au))
    moon_e = attr(default=0)  # eccentricity of lunar orbit
    # radius of the rocky core
    core_radius = attr(factory=lambda: 0*km, repr=quantity_formatter(km))
    # equatorial radius
    radius = attr(factory=lambda: 0*km, repr=quantity_formatter(km))
    orbit_zone = attr(default=0)  # the 'zone' of the planet
    density = attr(default=0)  # density (in g/cc)
    orb_period = attr(default=0)  # length of the local year (days)
    day = attr(default=0)  # length of the local day (hours)
    resonant_period = attr(default=0)  # TRUE if in resonant rotation
    esc_velocity = attr(default=0)  # units of cm/sec
    surf_accel = attr(default=0)  # units of cm/sec2
    surf_grav = attr(default=0)  # units of Earth gravities
    rms_velocity = attr(default=0)  # units of cm/sec
    molec_weight = attr(default=0)  # smallest molecular weight retained
    volatile_gas_inventory = attr(default=0)
    surf_pressure = attr(default=0)  # units of millibars (mb)
    greenhouse_effect = attr(default=0)  # runaway greenhouse effect?
    # the boiling po of water (Kelvin)
    boil_po = attr(factory=lambda: 0*K, repr=quantity_formatter(K))
    albedo = attr(default=0)  # albedo of the planet
    exospheric_temp = attr(factory=lambda: 0*K, repr=quantity_formatter(K))
    # quick non-iterative estimate
    estimated_temp = attr(factory=lambda: 0*K, repr=quantity_formatter(K))
    # for terrestrial moons and the like
    estimated_terr_temp = attr(factory=lambda: 0*K, repr=quantity_formatter(K))
    # surface temperature in Kelvin
    surf_temp = attr(factory=lambda: 0*K, repr=quantity_formatter(K))
    # Temperature rise due to greenhouse
    greenhs_rise = attr(factory=lambda: 0*K, repr=quantity_formatter(K))
    # Day-time temperature
    high_temp = attr(factory=lambda: 0*K, repr=quantity_formatter(K))
    # Night-time temperature
    low_temp = attr(factory=lambda: 0*K, repr=quantity_formatter(K))
    max_temp = attr(factory=lambda: 0*K,
                    repr=quantity_formatter(K))  # Summer/Day
    min_temp = attr(factory=lambda: 0*K,
                    repr=quantity_formatter(K))  # Winter/Night
    hydrosphere = attr(default=0)  # fraction of surface covered
    cloud_cover = attr(default=0)  # fraction of surface covered
    ice_cover = attr(default=0)  # fraction of surface covered
    sun = attr(default=0)
    atmosphere = attr(default=None)
    type = attr(default=PlanetType.UNKNOWN)  # Type code

    #   ZEROES end here

    def __repr__(self):
        if self.atmosphere is None:
            atmosphere_string = "No Atmosphere"
        else:
            atmosphere_string = tabulate([[gas.symbol,
                                           quantity_repr(amount, atm)]
                                          for gas, amount in self.atmosphere])

        repr_table = [
            ['Type', self.type],
            ['Mass', mass_repr(self.mass)],
            ['Radius', quantity_repr(self.radius, km)],
            ['Orbit', self.orbit],
            ['Surface gravity', quantity_repr(self.surf_grav, g_force)],
            [
                'Surface pressure',
                quantity_repr(self.surf_pressure, atm)
            ],
            ['Atmosphere', atmosphere_string],
        ]
        if len(self.moons) > 0:
            repr_table.append(['Moons', '\n'.join(repr(moon) for moon in self.moons)])
        return tabulate(repr_table)
