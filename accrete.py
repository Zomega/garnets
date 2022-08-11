from constants import DUST_DENSITY_COEFF, ALPHA, N, K
from math import sqrt, exp, pi


class CircumstellarDustLane:
    def __init__(self, inner_edge, outer_edge, dust_present, gas_present):
        self.inner = inner_edge
        self.outer = outer_edge
        self.dust_present = dust_present
        self.gas_present = gas_present

    def __repr__(self):
        return "\tINNER: " + str(self.inner) + ", OUTER: " + str(self.outer) + " D:" + str(self.dust_present) + "\n"


class CircumstellarDisk:
    def __init__(self, star):
        self.star = star
        self.planet_inner_bound = 0.01 * (star.mass_ratio ** 0.333) #SM - inner edge of disk? 0.3 AU, scales with stellar mass
        self.planet_outer_bound = 50 * (star.mass_ratio ** 0.333)  #SM - outer edge of disk? 50 AU, scales with stellar mass 

        self.lanes = [CircumstellarDustLane(
            0, star.stellar_dust_limit, True, True)] #SM - stellar dust limit is outer edge of Disk; in stellar_system.py; = 200 * starmass ^ 1/3; 1 solar mass is 200 AU

    def dust_density(self, a):
        return DUST_DENSITY_COEFF * sqrt(self.star.mass_ratio) * exp(-ALPHA * (a ** (1.0 / N))) 
        #SM - something to tune? certinaly get in a shape to compare with Mulders 2020. What even are these units?

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
            if not lane.dust_present:
                dust_density = 0.0
                gas_density = 0.0
            else:
                dust_density = self.dust_density(planetoid.orbit.a)
                if planetoid.mass < planetoid.critical_mass or (not lane.gas_present):
                    gas_density = 0.0
                else:
                    # TODO: This is DEEP Magic. Figure it out somehow.
                    gas_density = (K - 1.0) * dust_density / (1.0 + sqrt(planetoid.critical_mass / planetoid.mass) * (K - 1.0))
                    #SM - this is weird.

                # Compute the width of the overlap between the region of effect and the lane.
                bandwidth = planetoid.outer_effect_limit - planetoid.inner_effect_limit

                width = min(lane.outer, planetoid.outer_effect_limit) - max(lane.inner, planetoid.inner_effect_limit)

                temp1 = planetoid.outer_effect_limit - lane.outer
                if (temp1 < 0.0):
                    temp1 = 0.0

                temp2 = lane.inner - planetoid.inner_effect_limit
                if (temp2 < 0.0):
                    temp2 = 0.0

                temp = 4.0 * pi * (planetoid.orbit.a ** 2.0) * planetoid.reduced_mass * (1.0 - planetoid.orbit.e * (temp1 - temp2) / bandwidth)
                volume = temp * width
                #SM Here is the step of determining mass of dust in the lane that gets added without timestep to the planet. 
                # 4*pi*r**2

                new_dust_mass += volume * dust_density #a mass;
                new_gas_mass += volume * gas_density   #a mass 
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
                new_lanes.append(CircumstellarDustLane(
                    lane.inner, planetoid.inner_effect_limit, lane.dust_present, lane.gas_present))
            if lane.outer > planetoid.outer_effect_limit:
                print("OUTER")
                # Make an lane for the outside of the old lane
                new_lanes.append(CircumstellarDustLane(
                    lane.outer, planetoid.outer_effect_limit, lane.dust_present, lane.gas_present))
            # Make a lane for the overlapped portion.
            new_lanes.append(CircumstellarDustLane(max(lane.inner, planetoid.inner_effect_limit), min(
                lane.outer, planetoid.outer_effect_limit), False, gas and lane.gas_present))
        self.lanes = new_lanes

    def accrete_dust(self, planetoid):
        last_mass = planetoid.mass
        while True:
            new_dust_mass, new_gas_mass = self.collect_dust(planetoid)
            planetoid.dust_mass = new_dust_mass
            planetoid.gas_mass = new_gas_mass
            print((planetoid.mass - last_mass) / last_mass)
            # Accretion has slowed enough. Stop trying.
            if (planetoid.mass - last_mass) < (0.0001 * last_mass):
                break
            last_mass = planetoid.mass
        print("Accretion halted at ", planetoid.mass)
        self.update_dust_lanes(planetoid)
