from constants import DISK_ECCENTRICITY
from constants import B
from constants import SUN_MASS_IN_MOON_MASSES
from constants import SUN_MASS_IN_EARTH_MASSES
from constants import SUN_MASS_IN_JUPITER_MASSES
from math import sqrt
from attr import attrs, attrib
import attr


@attrs
class Star():
    mass_ratio = attrib()
    age = attrib()

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
            "\tMass: " + mass_repr() + "; Orbit: " + str(self.a) +
            " AU, Moons: " + str(len(self.moons)) + "\n"
        )


@attrs
class Protomoon(Planetoid):
    protoplanet = attrib()


class Planet():
    pass
