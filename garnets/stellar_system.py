import attr

from attr import attr
from attr import attrs
from constants import B
from constants import DISK_ECCENTRICITY
from constants import MILLIBARS_PER_ATM
from constants import SUN_MASS_IN_EARTH_MASSES
from constants import SUN_MASS_IN_JUPITER_MASSES
from constants import SUN_MASS_IN_MOON_MASSES
from enviroment import PlanetType
from math import sqrt
from tabulate import tabulate


@attrs(repr=False)
class Star():
    mass_ratio = attr()
    age = attr()

    name = attr(default="Unnamed Star")

    planets = attr(factory=list)

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
        return 200.0 * (self.mass_ratio**0.3333)

    @property
    def r_ecosphere(self):  # Source: StarGen, TODO Name? Value?
        return sqrt(self.luminosity_ratio)

    @property
    def life(self):  # Source: StarGen, TODO Name? Value?
        return 10**10 * (self.mass_ratio / self.luminosity_ratio)

    def __repr__(self):
        return self.name + ": mass = " + str(
            self.mass_ratio) + " solar mass; age = " + str(
                self.age) + '\n' + '\n'.join(
                    [repr(planet) for planet in self.planets])


@attrs
class StellarSystem:
    star = attr()
    planets = attr()


@attrs(repr=False)
class Orbit:
    a = attr()  # semi-major axis of solar orbit (in AU)
    e = attr()  # eccentricity of solar orbit

    @property
    def periapsis(self):
        return (1 - self.e) * self.a

    @property
    def apoapsis(self):
        return (1 + self.e) * self.a

    def __repr__(self):
        return 'a = ' + str(self.a) + ' e = ' + str(self.e)


@attrs
class Planetoid():
    orbit = attr()
    dust_mass = attr()
    gas_mass = attr()

    @property
    def mass(self):
        return self.dust_mass + self.gas_mass

    @property
    def reduced_mass(self):
        # To understand what this is all about...
        # http://spiff.rit.edu/classes/phys440/lectures/reduced/reduced.html
        # But some sort of 3 body case, see dole.
        # TODO: Understand better?
        return (self.mass / (1.0 + self.mass))**0.25

    @property
    def inner_effect_limit(self):
        temp = (self.orbit.a * (1.0 - self.orbit.e) * (1.0 - self.mass) /
                (1.0 + DISK_ECCENTRICITY))
        if temp < 0:
            return 0
        return temp

    @property
    def outer_effect_limit(self):
        return (self.orbit.a * (1.0 + self.orbit.e) * (1.0 + self.mass) /
                (1.0 - DISK_ECCENTRICITY))


@attrs
class Planetesimal(Planetoid):
    disk = attr()

    @property
    def critical_mass(self):
        perihelion_dist = self.orbit.a * (1.0 - self.orbit.e)
        temp = perihelion_dist * sqrt(self.disk.star.luminosity_ratio)
        return B * (temp**-0.75)


def mass_repr(mass):
    if mass * SUN_MASS_IN_MOON_MASSES <= 50:
        return str(mass * SUN_MASS_IN_MOON_MASSES) + " M_moon"
    if mass * SUN_MASS_IN_EARTH_MASSES <= 50:
        return str(mass * SUN_MASS_IN_EARTH_MASSES) + " M_earth"
    return str(mass * SUN_MASS_IN_JUPITER_MASSES) + " M_jupiter"


@attrs(repr=False)
class Protoplanet(Planetoid):
    star = attr()
    moons = attr(factory=list)

    def add_moon(self, moon):
        self.moons.append(moon)

    @property
    def mass_of_moons(self):
        return sum([moon.mass for moon in self.moons])

    @property
    def critical_mass(self):
        perihelion_dist = self.orbit.a * (1.0 - self.orbit.e)
        temp = perihelion_dist * sqrt(self.star.luminosity_ratio)
        return B * (temp**-0.75)

    def __repr__(self):

        return ("\tMass: " + mass_repr(self.mass) + " = attr() Orbit: " +
                str(self.orbit.a) + " AU, Moons: " + str(len(self.moons)) +
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

    axial_tilt = attr()  # units of degrees
    mass = attr()  # mass (in solar masses)
    dust_mass = attr()  # mass, ignoring gas
    gas_mass = attr()  # mass, ignoring dust

    moons = attr(factory=list)

    #   ZEROES start here -- TODO(woursler): A bunch of these should be other Zero-like types.
    gas_giant = attr(default=False)  # TRUE if the planet is a gas giant
    moon_a = attr(default=0)  # semi-major axis of lunar orbit (in AU)
    moon_e = attr(default=0)  # eccentricity of lunar orbit
    core_radius = attr(default=0)  # radius of the rocky core (in km)
    radius = attr(default=0)  # equatorial radius (in km)
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
    boil_po = attr(default=0)  # the boiling po of water (Kelvin)
    albedo = attr(default=0)  # albedo of the planet
    exospheric_temp = attr(default=0)  # units of degrees Kelvin
    estimated_temp = attr(default=0)  # quick non-iterative estimate (K)
    # for terrestrial moons and the like
    estimated_terr_temp = attr(default=0)
    surf_temp = attr(default=0)  # surface temperature in Kelvin
    greenhs_rise = attr(default=0)  # Temperature rise due to greenhouse
    high_temp = attr(default=0)  # Day-time temperature
    low_temp = attr(default=0)  # Night-time temperature
    max_temp = attr(default=0)  # Summer/Day
    min_temp = attr(default=0)  # Wer/Night
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
                                           str(amount) + ' mb']
                                          for gas, amount in self.atmosphere])
        return tabulate([
            ['Type', self.type],
            ['Mass', mass_repr(self.mass)],
            ['Radius', str(self.radius) + " km"],
            ['Orbit', self.orbit],
            ['Surface gravity', str(self.surf_grav) + ' g'],
            [
                'Surface pressure',
                str(self.surf_pressure / MILLIBARS_PER_ATM) + ' atm'
            ],
            ['Atmosphere', atmosphere_string],
            [
                'Moons', '\n'.join(repr(moon) for moon in self.moons)
                if len(self.moons) > 0 else 'No Moons'
            ],
        ])
