from constants import DISK_ECCENTRICITY
from constants import B
from constants import SUN_MASS_IN_MOON_MASSES
from constants import SUN_MASS_IN_EARTH_MASSES
from constants import SUN_MASS_IN_JUPITER_MASSES
from math import sqrt
from attr import attrs, attrib
import attr
from enviroment import PlanetType


@attrs
class Star():
    mass_ratio = attrib()
    age = attrib()

    name = attrib(default="Unnamed Star")

    @property
    # Approximates the luminosity of the star.
    # TODO: express only as ratio?
    # Source: http://en.wikipedia.org/wiki/Mass%E2%80%93luminosity_relation
    def luminosity_ratio(self):
        if (self.mass_ratio < .43):
            return .23 * (self.mass_ratio ** 2.3)
        if (self.mass_ratio < 2):
            return (self.mass_ratio ** 4)
        # Main Sequence Stars
        if (self.mass_ratio < 20):
            return 1.5 * (self.mass_ratio ** 3.5)
        # For HUGE stars...
        return 3200 * self.mass_ratio

    @property
    # Source: StarGen, TODO Verify against current data.
    def stellar_dust_limit(self):
        return 200.0 * (self.mass_ratio ** 0.3333)

    @property
    def r_ecosphere(self):  # Source: StarGen, TODO Name? Value?
        return sqrt(self.luminosity_ratio)

    @property
    def life(self):  # Source: StarGen, TODO Name? Value?
        return 10**10 * (self.mass_ratio / self.luminosity_ratio)


@attrs
class StellarSystem:
    star = attrib()
    planets = attrib()


@attrs
class Planetoid():
    a = attrib()
    e = attrib()
    dust_mass = attrib()
    gas_mass = attrib()

    @property
    def mass(self):
        return self.dust_mass + self.gas_mass

    @property
    def reduced_mass(self):
        # To understand what this is all about...
        # http://spiff.rit.edu/classes/phys440/lectures/reduced/reduced.html
        # But some sort of 3 body case, see dole.
        # TODO: Understand better?
        return (self.mass / (1.0 + self.mass)) ** 0.25

    @property
    def inner_effect_limit(self):
        temp = (self.a * (1.0 - self.e) *
                (1.0 - self.mass) / (1.0 + DISK_ECCENTRICITY))
        if temp < 0:
            return 0
        return temp

    @property
    def outer_effect_limit(self):
        return (
            self.a *
            (1.0 + self.e) *
            (1.0 + self.mass) /
            (1.0 - DISK_ECCENTRICITY)
        )


@attrs
class Planetesimal(Planetoid):
    disk = attrib()

    @property
    def critical_mass(self):
        perihelion_dist = self.a * (1.0 - self.e)
        temp = perihelion_dist * sqrt(self.disk.star.luminosity_ratio)
        return B * (temp ** -0.75)


@attrs(repr=False)
class Protoplanet(Planetoid):
    star = attrib()
    moons = attrib(default=attr.Factory(list))

    def add_moon(self, moon):
        self.moons.append(moon)

    @property
    def mass_of_moons(self):
        return sum([moon.mass for moon in self.moons])

    @property
    def critical_mass(self):
        perihelion_dist = self.a * (1.0 - self.e)
        temp = perihelion_dist * sqrt(self.star.luminosity_ratio)
        return B * (temp ** -0.75)

    def __repr__(self):
        def mass_repr():
            if self.mass * SUN_MASS_IN_MOON_MASSES <= 50:
                return str(self.mass * SUN_MASS_IN_MOON_MASSES) + " M_moon"
            if self.mass * SUN_MASS_IN_EARTH_MASSES <= 50:
                return str(self.mass * SUN_MASS_IN_EARTH_MASSES) + " M_earth"
            return str(self.mass * SUN_MASS_IN_JUPITER_MASSES) + " M_jupiter"

        return (
            "\tMass: " + mass_repr() + " = attrib() Orbit: " + str(self.a) +
            " AU, Moons: " + str(len(self.moons)) + "\n"
        )


@attrs
class Protomoon(Planetoid):
    protoplanet = attrib()


# TODO(woursler): Go over these with a fine tooth comb. Many are not relevant, or only relevant during initialization.
# Many should be properties.
# Many should be initialized differently.
@attrs
class Planet():
    # Orbital details.
    a = attrib()  # semi-major axis of solar orbit (in AU)
    e = attrib()  # eccentricity of solar orbit

    axial_tilt = attrib()   # units of degrees
    mass = attrib()    # mass (in solar masses)
    dust_mass = attrib()   # mass, ignoring gas
    gas_mass = attrib()   # mass, ignoring dust

    #   ZEROES start here -- TODO(woursler): A bunch of these should be other Zero-like types.
    gas_giant = attrib(default=False)   # TRUE if the planet is a gas giant
    moon_a = attrib(default=0)    # semi-major axis of lunar orbit (in AU)
    moon_e = attrib(default=0)    # eccentricity of lunar orbit
    core_radius = attrib(default=0)  # radius of the rocky core (in km)
    radius = attrib(default=0)    # equatorial radius (in km)
    orbit_zone = attrib(default=0)   # the 'zone' of the planet
    density = attrib(default=0)   # density (in g/cc)
    orb_period = attrib(default=0)   # length of the local year (days)
    day = attrib(default=0)    # length of the local day (hours)
    resonant_period = attrib(default=0)  # TRUE if in resonant rotation
    esc_velocity = attrib(default=0)  # units of cm/sec
    surf_accel = attrib(default=0)   # units of cm/sec2
    surf_grav = attrib(default=0)   # units of Earth gravities
    rms_velocity = attrib(default=0)  # units of cm/sec
    molec_weight = attrib(default=0)  # smallest molecular weight retained
    volatile_gas_inventory = attrib(default=0)
    surf_pressure = attrib(default=0)  # units of millibars (mb)
    greenhouse_effect = attrib(default=0)  # runaway greenhouse effect?
    boil_po = attrib(default=0)   # the boiling po of water (Kelvin)
    albedo = attrib(default=0)    # albedo of the planet
    exospheric_temp = attrib(default=0)  # units of degrees Kelvin
    estimated_temp = attrib(default=0)     # quick non-iterative estimate (K)
    # for terrestrial moons and the like
    estimated_terr_temp = attrib(default=0)
    surf_temp = attrib(default=0)   # surface temperature in Kelvin
    greenhs_rise = attrib(default=0)  # Temperature rise due to greenhouse
    high_temp = attrib(default=0)   # Day-time temperature
    low_temp = attrib(default=0)   # Night-time temperature
    max_temp = attrib(default=0)   # Summer/Day
    min_temp = attrib(default=0)   # Wer/Night
    hydrosphere = attrib(default=0)  # fraction of surface covered
    cloud_cover = attrib(default=0)  # fraction of surface covered
    ice_cover = attrib(default=0)   # fraction of surface covered
    sun = attrib(default=0)
    atmosphere = attrib(default=0)
    type = attrib(default=PlanetType.UNKNOWN)    # Type code
    #   ZEROES end here
