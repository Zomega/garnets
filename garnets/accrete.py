from attr import attr
from attr import attrs
from constants import ALPHA
from constants import DUST_DENSITY_COEFF
from constants import GAS_DUST_RATIO
from math import exp
from math import pi
from math import sqrt
from xatu.core import quantity_formatter
from xatu.core import quantity_repr
from xatu.core import dimensionless_with_units
from xatu.units import au
from xatu.units import kg
from xatu.units import m, solar_mass
from typing import List
from stellar_system import mass_repr


@attrs
class CircumstellarDustLane:
    inner = attr(repr=quantity_formatter(au))
    outer = attr(repr=quantity_formatter(au))

    dust_present: bool = attr()
    gas_present: bool = attr()


@attrs
class CircumstellarDisk:
    star = attr()
    lanes: List[CircumstellarDustLane] = attr(default=None)

    @property
    def planet_inner_bound(self):
        # TODO(woursler): Confirm AU?
        return 0.3 * (self.star.mass_ratio**(1/3)) * au

    @property
    def planet_outer_bound(self):
        # TODO(woursler): Confirm AU?
        return 50 * (self.star.mass_ratio**(1/3)) * au

    def __attrs_post_init__(self):
        if self.lanes is None:
            self.lanes = [
                CircumstellarDustLane(
                    0*au,
                    self.star.stellar_dust_limit,
                    dust_present=True,
                    gas_present=True,
                )
            ]

    def dust_density(self, a):
        return (
            DUST_DENSITY_COEFF
            * sqrt(self.star.mass_ratio)
            * exp(
                -ALPHA * (dimensionless_with_units(a, au)**(1/3))
            )
            * solar_mass / au ** 3
        )  # TODO(woursler): Figure out the implicit units, include in DUST_DENSITY_COEFF

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
            if (lane.inner <= inner
                    and lane.outer > inner) or (lane.outer >= outer
                                                and lane.inner < outer):
                if lane.dust_present:
                    return True
        return False

    def collect_dust(self, planetoid):
        new_dust_mass = 0 * kg
        new_gas_mass = 0 * kg
        for lane in self.lanes:

            # If the lane doesn't overlap, then we should just continue.
            if (lane.outer <= planetoid.inner_effect_limit) or (
                    lane.inner >= planetoid.outer_effect_limit):
                continue

            # Now we need to figure out the density of gas and dust in the lane.
            if not lane.dust_present:
                dust_density = 0 * kg / m ** 3
                gas_density = 0 * kg / m ** 3
            else:
                dust_density = self.dust_density(planetoid.orbit.a)
                if planetoid.mass < planetoid.critical_mass or (
                        not lane.gas_present):
                    gas_density = 0 * kg / m ** 3
                else:
                    # TODO: This is DEEP Magic. Figure it out somehow.
                    gas_density = (GAS_DUST_RATIO - 1) * dust_density / (
                        1 + sqrt(planetoid.critical_mass / planetoid.mass) *
                        (GAS_DUST_RATIO - 1))

                # Compute the width of the overlap between the region of effect and the lane.
                bandwidth = planetoid.outer_effect_limit - planetoid.inner_effect_limit

                width = min(lane.outer, planetoid.outer_effect_limit) - \
                    max(lane.inner, planetoid.inner_effect_limit)

                temp1 = planetoid.outer_effect_limit - lane.outer
                if temp1 < 0 * m:
                    temp1 = 0 * m

                temp2 = lane.inner - planetoid.inner_effect_limit
                if temp2 < 0 *m:
                    temp2 = 0 * m

                temp = 4 * pi * (planetoid.orbit.a ** 2) * planetoid.reduced_mass * \
                    (1 - planetoid.orbit.e * (temp1 - temp2) / bandwidth)
                volume = temp * width

                new_dust_mass += volume * dust_density
                new_gas_mass += volume * gas_density
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
                new_lanes.append(
                    CircumstellarDustLane(lane.inner,
                                          planetoid.inner_effect_limit,
                                          lane.dust_present, lane.gas_present))
            if lane.outer > planetoid.outer_effect_limit:
                print("OUTER")
                # Make an lane for the outside of the old lane
                new_lanes.append(
                    CircumstellarDustLane(lane.outer,
                                          planetoid.outer_effect_limit,
                                          lane.dust_present, lane.gas_present))
            # Make a lane for the overlapped portion.
            new_lanes.append(
                CircumstellarDustLane(
                    max(lane.inner, planetoid.inner_effect_limit),
                    min(lane.outer, planetoid.outer_effect_limit),
                    dust_present=False,
                    gas_present=gas and lane.gas_present,
                )
            )
        self.lanes = new_lanes

    def accrete_dust(self, planetoid):
        last_mass = planetoid.mass
        while True:
            new_dust_mass, new_gas_mass = self.collect_dust(planetoid)
            planetoid.dust_mass = new_dust_mass
            planetoid.gas_mass = new_gas_mass
            print(
                "Growth since last step",
                round((planetoid.mass - last_mass) / last_mass, 2),
                "%"
            )
            # Accretion has slowed enough. Stop trying.
            if (planetoid.mass - last_mass) < (0.0001 * last_mass):
                break
            last_mass = planetoid.mass
        print("Accretion halted at %s." % mass_repr(planetoid.mass))
        self.update_dust_lanes(planetoid)
