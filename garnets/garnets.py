import logging
import math
import random

from math import exp
from math import inf as INCREDIBLY_LARGE_NUMBER
from math import log
from pathlib import Path

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import select_autoescape

from accrete import CircumstellarDisk
from chemtable import GASES
from chemtable import lookup_gas
from constants import ASTEROID_MASS_LIMIT
from constants import EARTH_ALBEDO
from constants import EARTH_AVERAGE_TEMP
from constants import EARTH_EXOSPHERE_TEMP
from constants import ECCENTRICITY_COEFF
from constants import FREEZING_POINT_OF_WATER
from constants import GAS_GIANT_ALBEDO
from constants import PROTOPLANET_MASS
from enviroment import PlanetType
from enviroment import acceleration
from enviroment import boiling_point
from enviroment import day_length
from enviroment import empirical_density
from enviroment import escape_vel
from enviroment import est_temp
from enviroment import gas_life
from enviroment import grnhouse
from enviroment import inclination
from enviroment import iterate_surface_temp
from enviroment import kothari_radius
from enviroment import min_molec_weight
from enviroment import orb_zone
from enviroment import period
from enviroment import rms_vel
from enviroment import vol_inventory
from enviroment import volume_density
from enviroment import volume_radius
from stellar_system import Orbit
from stellar_system import Planet
from stellar_system import Planetesimal
from stellar_system import Protomoon
from stellar_system import Protoplanet
from stellar_system import Star
from stellar_system import mass_repr
from xatu.core import dimensionless_with_units
from xatu.core import quantity_repr
from xatu.math import sqrt
from xatu.units import K
from xatu.units import atm
from xatu.units import au
from xatu.units import bar
from xatu.units import deg
from xatu.units import earth_mass
from xatu.units import hour
from xatu.units import kg
from xatu.units import km
from xatu.units import m
from xatu.units import millibar
from xatu.units import year

logging.getLogger().setLevel(logging.INFO)

VERBOSE = True  # TODO(woursler): Move to logging.


def random_star():  # TODO: Add seed?
    # Sources
    # exoplanets.co/exoplanet-correlations/host-star-mass-distribution.html
    # en.wikipedia.org/wiki/Main_sequence#mediaviewer/File:HRDiagram.png
    # TODO: Code up generation.
    age = random.randrange(1 * 10**9, 6 * 10**9) * year
    return Star(age=age, mass_ratio=1)


def generate_stellar_system(star, do_gases=True, do_moons=True):
    protoplanets = generate_planetary_masses(star,
                                             0.0,
                                             star.stellar_dust_limit,
                                             do_moons=do_moons)
    star.planets = [
        generate_planet(p, star, do_gases=do_gases, do_moons=do_moons)
        for p in protoplanets
        if p.mass > 0*kg
    ]
    return star


# Create protoplanets.


def random_planetesimal(disk):
    a = random.uniform(disk.planet_inner_bound, disk.planet_outer_bound)
    e = 1.0 - (random.uniform(0.0, 1.0)**ECCENTRICITY_COEFF)
    if e > .99:
        e = .99
    return Planetesimal(
        disk=disk,
        orbit=Orbit(
            a=a,
            e=e,
        ),
        dust_mass=PROTOPLANET_MASS,
        gas_mass=0,
    )


def generate_planetary_masses(star, inner_dust, outer_dust, do_moons=True):
    disk = CircumstellarDisk(star)

    planets = []

    sequential_failures = 0

    while disk.dust_left and sequential_failures < 10**3:
        canidate = random_planetesimal(disk)

        iel = canidate.inner_effect_limit
        oel = canidate.outer_effect_limit

        if disk.dust_available(iel, oel) > 0:
            sequential_failures = 0
            logging.info("Injecting planetesimal at %s..." %
                         quantity_repr(canidate.orbit.a, au))

            disk.accrete_dust(canidate)

            if canidate.mass > PROTOPLANET_MASS:
                coalesce_planetesimals(disk, planets, canidate, do_moons)
                logging.info("\tsuccess.")
            else:
                logging.info("\tfailed due to large neighbor.")
        else:
            sequential_failures += 1
    return planets


def convert_planetesimal_to_protoplanet(planetesimal):
    return Protoplanet(star=planetesimal.disk.star,
                       orbit=planetesimal.orbit,
                       dust_mass=planetesimal.dust_mass,
                       gas_mass=planetesimal.gas_mass)


def convert_planetesimal_to_protomoon(planetesimal, planet):
    print("Capturing a protomoon.")
    return Protomoon(
        protoplanet=planet,
        orbit=Orbit(
            a=None,
            e=None,
        ),
        dust_mass=planetesimal.dust_mass,
        gas_mass=planetesimal.gas_mass,
    )


def coalesce_planetesimals(disk, planets, canidate, do_moons):
    finished = False

    # First we try to find an existing planet with an over-lapping orbit.
    for planet in planets:
        print("Out of order", planet, canidate)

        diff = planet.orbit.a - canidate.orbit.a

        if diff > 0 * m:
            dist1 = canidate.orbit.apoapsis * \
                (1 + canidate.reduced_mass) - canidate.orbit.a
            # x aphelion
            dist2 = planet.orbit.a - (planet.orbit.periapsis *
                                      (1 - planet.reduced_mass))
        else:
            dist1 = canidate.orbit.a - (canidate.orbit.periapsis *
                                        (1 - canidate.reduced_mass))
            # x perihelion
            dist2 = (planet.orbit.apoapsis *
                     (1 + planet.reduced_mass)) - planet.orbit.a

        if abs(diff) <= abs(dist1) or abs(diff) <= abs(dist2):
            # Figure out the new orbit.
            a = (planet.mass + canidate.mass) / \
                ((planet.mass / planet.orbit.a) +
                 (canidate.mass / canidate.orbit.a))

            temp = planet.mass * sqrt(
                planet.orbit.a) * sqrt(1 - (planet.orbit.e**2))
            temp = temp + (canidate.mass * sqrt(canidate.orbit.a) *
                           sqrt(sqrt(1 - (canidate.orbit.e**2))))
            temp = temp / (
                (planet.mass + canidate.mass) * sqrt(canidate.orbit.a))
            temp = 1 - (temp**2)
            if temp < 0 or temp >= 1:
                temp = 0
            e = sqrt(temp)

            if do_moons:
                if canidate.mass < canidate.critical_mass:
                    if canidate.mass < 2.5 * earth_mass \
                            and canidate.mass > .0001 * earth_mass \
                            and planet.mass_of_moons < planet.mass * .05 \
                            and planet.mass > canidate.mass:
                        # TODO: Refactor moon capture logic. If `canidate.mass > planet.mass`,
                        # swap `candidate` and `planet` to ensure the more massive body is treated
                        # as the primary object capturing the smaller one as a moon.
                        # This avoids the `planet.mass > canidate.mass` check.
                        planet.add_moon(
                            convert_planetesimal_to_protomoon(
                                canidate, planet))
                        logging.info(
                            "Moon captured at %s. Planet Mass: %s, Moon mass: %s." % (
                                quantity_repr(planet.orbit.a, au),
                                mass_repr(planet.mass),
                                mass_repr(canidate.mass)
                            )
                        )
                        finished = True
                        break
                    else:
                        # TODO: Enhance logging for failed moon capture. Specify which condition(s)
                        # (e.g., candidate mass too high/low, planet's existing moon mass too high,
                        # candidate more massive than planet) prevented capture.
                        logging.info(
                            "Did not capture potential moon at %s. Conditions not met or collision imminent." % quantity_repr(
                                planet.orbit.a, au)
                        )

            logging.info(
                "Collision between two planetesimals! Computing new orbit and accumulating additional mass."
            )

            planet.orbit = Orbit(a=a, e=e)
            planet.dust_mass = planet.dust_mass + canidate.dust_mass  # + new_dust
            planet.gas_mass = planet.gas_mass + canidate.gas_mass  # + new_gas
            finished = True

            # TODO: Consider refactoring the post-collision accretion step.
            # Instead of immediate re-accretion via `disk.accrete_dust(planet)`,
            # explore marking the planet as 'dirty' or 'needs_re_accretion' to
            # handle this in a subsequent simulation phase. This could allow for
            # more complex interactions or batch processing of accretion events.
            disk.accrete_dust(planet)

            logging.info("Conglomerate is now %s at %s." % (
                mass_repr(planet.mass),
                quantity_repr(planet.orbit.a, au)
            ))

    if not finished:
        # TODO: Enhance logging for new protoplanet formation. Include
        # additional information such as its mass and potentially key
        # compositional details (e.g., dust/gas ratio if available).
        logging.info("New Protoplanet formed at %s with mass %s." %
                     (quantity_repr(canidate.orbit.a, au), mass_repr(canidate.mass)))
        planets.append(convert_planetesimal_to_protoplanet(canidate))


def calculate_gases(star, planet, planet_id):
    if planet.surf_pressure > 0 * atm:

        amount = [0 for _ in range(len(GASES))]
        totamount = 0
        pressure = dimensionless_with_units(planet.surf_pressure, bar)
        n = 0

        for i in range(len(GASES)):

            # TODO: Clarify the derivation and meaning of the variable `yp`
            # and the formula used for its calculation. This formula appears to adjust
            # boiling points based on pressure. Document the source of the constants
            # (e.g., -5050.5, 373., 0.001) and explain its physical basis
            # (e.g., Clausius-Clapeyron approximation for water, adapted for other gases).
            yp = GASES[i].boil / \
                (373. * ((log((pressure) + 0.001) / -5050.5) + (1.0 / 373.)))

            if ((yp >= 0*K and yp < planet.low_temp)
                    and (GASES[i].weight >= planet.molec_weight)):

                vrms = rms_vel(GASES[i].weight, planet.exospheric_temp)
                pvrms = pow(1 / (1 + vrms / planet.esc_velocity),
                            star.age / 1e9 / year)
                abund = GASES[i].abunds  # GASES[i].abunde
                react = 1.0
                fract = 1.0
                pres2 = 1.0

                # TODO: Refactor gas reactivity logic. Move the hardcoded rules
                # for specific gases (Ar, He, O, O2, CO2) and their dependence on
                # stellar age and pressure into `chemtable.py`, possibly by adding
                # reactivity parameters or functions to the `Gas` class or a
                # related data structure. This would centralize chemical properties.

                if GASES[i].symbol == "Ar":
                    react = .15 * star.age / 4e9 / year

                elif GASES[i].symbol == "He":

                    abund = abund * (0.001 + (planet.gas_mass / planet.mass))
                    pres2 = (0.75 + pressure)
                    react = pow(1 / (1 + GASES[i].reactivity),
                                star.age / 2e9 / year * pres2)

                elif (
                        GASES[i].symbol == "O" or GASES[i].symbol == "O2"
                ) and star.age > 2e9 * year and planet.surf_temp > 270 * K and planet.surf_temp < 400 * K:
                    pres2 = (0.89 + pressure / 4)
                    react = pow(1 / (1 + GASES[i].reactivity),
                                pow(star.age / 2e9 / year, 0.25) * pres2)

                elif GASES[
                        i].symbol == "CO2" and star.age > 2e9 * year and planet.surf_temp > 270 * K and planet.surf_temp < 400 * K:
                    pres2 = (0.75 + pressure)
                    react = pow(1 / (1 + GASES[i].reactivity),
                                pow(star.age / 2e9 / year, 0.5) * pres2)
                    react *= 1.5

                else:
                    pres2 = 0.75 + pressure
                    react = pow(1 / (1 + GASES[i].reactivity),
                                star.age / 2e9 / year * pres2)

                fract = (1 - (planet.molec_weight / GASES[i].weight))

                amount[i] = abund * pvrms * react * fract
                '''if ((flag_verbose & 0x4000) and
                    (strcmp(GASES[i].symbol, "O") == 0 or
                     strcmp(GASES[i].symbol, "N") == 0 or
                     strcmp(GASES[i].symbol, "Ar") == 0 or
                     strcmp(GASES[i].symbol, "He") == 0 or
                     strcmp(GASES[i].symbol, "CO2") == 0))

                    fprintf (stderr, "%-5.2Lf %-3.3s, %-5.2Lf = a %-5.2Lf * p %-5.2Lf * r %-5.2Lf * p2 %-5.2Lf * f %-5.2Lf\t(%.3Lf%%)\n",
                              planet.mass * SUN_MASS_IN_EARTH_MASSES,
                              GASES[i].symbol,
                              amount[i],
                              abund,
                              pvrms,
                              react,
                              pres2,
                              fract,
                              100.0 * (planet.gas_mass / planet.mass)
                             )'''

                totamount += amount[i]
                if (amount[i] > 0.0):
                    n += 1

            else:
                amount[i] = 0.0

        if n > 0:

            planet.gases = n
            planet.atmosphere = []

            for i in range(len(GASES)):

                if amount[i] > 0.0:

                    planet.atmosphere.append(
                        (
                            GASES[i],
                            planet.surf_pressure * amount[i] / totamount,
                        )
                    )

                    '''if (flag_verbose & 0x2000)

                        if ((planet.atmosphere[n].num == AN_O) and
                            inspired_partial_pressure (planet.surf_pressure,
                                                       planet.atmosphere[n].surf_pressure)
                            > GASES[i].max_ipp)

                            fprintf (stderr, "%s\t Poisoned by O2\n",
                                     planet_id)'''

                    n += 1

            # TODO(woursler): sort planet.atmosphere
            '''if (flag_verbose & 0x0010):

                fprintf (stderr, "\n%s (%5.1Lf AU) gases:\n",
                        planet_id, planet.orbit.a)

                for (i = 0; i < planet.gases; i++)

                    fprintf (stderr, "%3d: %6.1Lf, %11.7Lf%%\n",
                            planet.atmosphere[i].num,
                            planet.atmosphere[i].surf_pressure,
                            100. * (planet.atmosphere[i].surf_pressure /
                                    planet.surf_pressure)
                            )'''


def roche_limit(planet, moon):
    return planet.radius * (2 * planet.density / moon.density) ** (1/3)


def hill_sphere(planet, star):
    # TODO: The formula used is a common approximation for the Hill sphere
    # radius ( R_H = a * (m / (3*M))^(1/3) ). Confirm if this level of precision
    # is adequate for the simulation or if more exact formulations are needed for
    # specific scenarios (e.g., highly eccentric orbits, larger moon/planet mass ratios).
    return planet.orbit.a * pow(
        (planet.mass / (3.0 * star.mass)), (1.0 / 3.0))


def generate_planet(protoplanet,
                    star,
                    random_tilt=0,
                    planet_id=None,
                    do_gases=True,
                    do_moons=True,
                    is_moon=False):
    planet = Planet(
        sun=star,
        orbit=protoplanet.orbit,
        dust_mass=protoplanet.dust_mass,
        gas_mass=protoplanet.gas_mass,
        mass=protoplanet.mass,
        axial_tilt=inclination(
            protoplanet.orbit.a) if random_tilt else 0 * deg,
        atmosphere=None,
        surf_temp=0 * K,
        high_temp=0 * K,
        low_temp=0 * K,
        max_temp=0 * K,
        min_temp=0 * K,
        greenhs_rise=0,
        resonant_period=False,
        orbit_zone=orb_zone(star.luminosity_ratio, protoplanet.orbit.a),
        orb_period=period(protoplanet.orbit.a, protoplanet.mass,
                          star.mass))

    planet.exospheric_temp = EARTH_EXOSPHERE_TEMP / \
        ((planet.orbit.a / star.r_ecosphere) ** 2)
    planet.rms_velocity = rms_vel(lookup_gas(
        'N2').weight, planet.exospheric_temp)
    planet.core_radius = kothari_radius(planet.dust_mass, False,
                                        planet.orbit_zone)

    # Calculate the radius as a gas giant, to verify it will retain gas.
    # Then if mass > Earth, it's at least 5% gas and retains He, it's
    # some flavor of gas giant.

    planet.density = empirical_density(planet.mass, planet.orbit.a,
                                       star.r_ecosphere, True)
    planet.radius = volume_radius(planet.mass, planet.density)

    planet.surf_accel = acceleration(planet.mass, planet.radius)
    # TODO: Clarify the distinction between `surf_accel` (calculated
    # from M, R) and `surf_grav`. If they are intended to be identical
    # (gravitational acceleration at the surface), consider using only one
    # variable (e.g., `surface_gravity`). If `surf_grav` might later include
    # other effects (e.g., centrifugal due to rotation), document this.
    planet.surf_grav = planet.surf_accel

    planet.molec_weight = min_molec_weight(planet)

    if ((planet.mass > 1 * earth_mass)
            # TODO: Document the source or rationale for the 0.05 (5%)
            # gas mass fraction threshold used in classifying gas giant types.
            # Cite relevant planetary science literature or model assumptions.
            and ((planet.gas_mass / planet.mass) > 0.05)
            and (planet.molec_weight <= lookup_gas('He').weight)):

        if ((planet.gas_mass / planet.mass) < 0.20):
            planet.type = PlanetType.SUB_SUB_GAS_GIANT
        elif (planet.mass < 20 * earth_mass):
            planet.type = PlanetType.SUB_GAS_GIANT
        else:
            planet.type = PlanetType.GAS_GIANT

    else:  # If not, it's rocky.

        planet.radius = kothari_radius(planet.mass, False, planet.orbit_zone)
        planet.density = volume_density(planet.mass, planet.radius)

        planet.surf_accel = acceleration(planet.mass, planet.radius)
        planet.surf_grav = planet.surf_accel

        if ((planet.gas_mass / planet.mass) > 0.000001):

            h2_mass = planet.gas_mass * 0.85
            he_mass = (planet.gas_mass - h2_mass) * 0.999

            h2_loss = 0.0
            he_loss = 0.0

            h2_life = gas_life(lookup_gas('H'), planet)
            he_life = gas_life(lookup_gas('He'), planet)

            if (h2_life < star.age):

                h2_loss = ((1.0 - (1.0 / exp(star.age / h2_life))) * h2_mass)

                planet.gas_mass -= h2_loss
                planet.mass -= h2_loss

                planet.surf_accel = acceleration(planet.mass, planet.radius)
                planet.surf_grav = planet.surf_accel

            if (he_life < star.age):

                he_loss = ((1.0 - (1.0 / exp(star.age / he_life))) * he_mass)

                planet.gas_mass -= he_loss
                planet.mass -= he_loss

                planet.surf_accel = acceleration(planet.mass, planet.radius)
                planet.surf_grav = planet.surf_accel
            '''if (((h2_loss + he_loss) > .000001) and (flag_verbose & 0x0080)):
                fprintf(stderr, "%s\tLosing gas: H2: %5.3Lf EM, He: %5.3Lf EM\n",
                        planet_id,
                        h2_loss * SUN_MASS_IN_EARTH_MASSES, he_loss * SUN_MASS_IN_EARTH_MASSES)'''

    planet.day = day_length(planet)  # Modifies planet.resonant_period
    planet.esc_velocity = escape_vel(planet.mass, planet.radius)

    if planet.type == PlanetType.GAS_GIANT or planet.type == PlanetType.SUB_GAS_GIANT or planet.type == PlanetType.SUB_SUB_GAS_GIANT:

        planet.greenhouse_effect = False
        planet.volatile_gas_inventory = INCREDIBLY_LARGE_NUMBER
        planet.surf_pressure = INCREDIBLY_LARGE_NUMBER * atm

        planet.boil_point = INCREDIBLY_LARGE_NUMBER * K

        planet.surf_temp = INCREDIBLY_LARGE_NUMBER * K
        planet.greenhs_rise = 0
        planet.albedo = random.uniform(GAS_GIANT_ALBEDO - 0.1, GAS_GIANT_ALBEDO + 0.1)
        planet.hydrosphere = 1.0
        planet.cloud_cover = 1.0
        planet.ice_cover = 0.0
        planet.surf_grav = planet.surf_accel
        planet.molec_weight = min_molec_weight(planet)
        planet.estimated_temp = est_temp(star.r_ecosphere, planet.orbit.a,
                                         planet.albedo)
        planet.estimated_terr_temp = est_temp(star.r_ecosphere, planet.orbit.a,
                                              EARTH_ALBEDO)

        temp = planet.estimated_terr_temp

        if (temp >= FREEZING_POINT_OF_WATER) and (
                temp <= EARTH_AVERAGE_TEMP + 10 * K) and (star.age > 2.0E9 * year):
            if VERBOSE:
                print(
                    "%s\t%s (%s, %s old)%s with earth-like temperature (%s)." % (
                        planet_id,
                        str(planet.type),
                        mass_repr(planet.mass),
                        quantity_repr(star.age, year),
                        "" if planet.first_moon == None else " with moon",
                        quantity_repr(temp, K),
                    )
                )
    else:

        planet.estimated_temp = est_temp(star.r_ecosphere, planet.orbit.a,
                                         EARTH_ALBEDO)
        planet.estimated_terr_temp = est_temp(star.r_ecosphere, planet.orbit.a,
                                              EARTH_ALBEDO)

        planet.surf_grav = planet.surf_accel
        planet.molec_weight = min_molec_weight(planet)

        planet.greenhouse_effect = grnhouse(star.r_ecosphere, planet.orbit.a)
        planet.volatile_gas_inventory = vol_inventory(
            planet.mass, planet.esc_velocity, planet.rms_velocity,
            star.mass_ratio, planet.orbit_zone, planet.greenhouse_effect,
            (planet.gas_mass / planet.mass) > 0.000001)
        planet.surf_pressure = 1 * atm

        # TODO(woursler): Renable?
        '''with_units(
            pressure(
                planet.volatile_gas_inventory,
                planet.radius,
                planet.surf_grav,
            ),
            atm,
        )'''
    # TODO: Review the surface pressure calculation for rocky planets.
    # Currently, it's set to a fixed `1 * atm` before `iterate_surface_temp`.
    # Evaluate if the commented-out detailed `pressure(...)` calculation
    # (based on `volatile_gas_inventory`) should be re-enabled and integrated
    # into the iteration loop for a self-consistent atmosphere model.

        if planet.surf_pressure == 0 * atm:
            planet.boil_point = 0 * K
        else:
            planet.boil_point = boiling_point(planet.surf_pressure)

        # Sets:
        # planet.surf_temp
        # planet.greenhs_rise
        # planet.albedo
        # planet.hydrosphere
        # planet.cloud_cover
        # planet.ice_cover
        iterate_surface_temp(planet)

        if (do_gases and (planet.max_temp >= FREEZING_POINT_OF_WATER)
                and (planet.min_temp <= planet.boil_point)):
            calculate_gases(star, planet, planet_id)

        # Next we assign a type to the planet.

        # TODO: Critical: Ensure consistent units for `planet.surf_pressure`.
        # It's initialized in `atm` (e.g. `1 * atm` or `INCREDIBLY_LARGE_NUMBER * atm`)
        # but compared with `millibar` values in type classification (e.g. `< 1 * millibar`).
        # Convert values to a consistent unit (e.g., millibar or atm) before
        # comparison to ensure correct planet type assignment.
        if (planet.surf_pressure < 1 * millibar): # Assuming surf_pressure is converted to mbar for this block
            if (not is_moon) and planet.mass < ASTEROID_MASS_LIMIT:
                planet.type = PlanetType.ASTERIODS
            else:
                planet.type = PlanetType.ROCK

        elif planet.surf_pressure > 6000 * millibar \
                and planet.molec_weight <= lookup_gas('H2').weight:  # Retains Hydrogen

            planet.type = PlanetType.SUB_SUB_GAS_GIANT
            planet.gases = 0
            planet.atmosphere = None

        else:
            # Atmospheres:
            if (int(dimensionless_with_units(planet.day, hour))
                    == int(dimensionless_with_units(planet.orb_period, hour))) \
                    or planet.resonant_period:
                planet.type = PlanetType.TIDALLY_LOCKED
            elif (planet.hydrosphere >= 0.95):
                planet.type = PlanetType.WATER  # >95% water
            elif (planet.ice_cover >= 0.95):
                planet.type = PlanetType.ICE  # >95% ice
            elif (planet.hydrosphere > 0.05):
                planet.type = PlanetType.TERRESTRIAL  # Terrestrial
                # else <5% water
            elif (planet.max_temp > planet.boil_point):
                planet.type = PlanetType.VENUSIAN  # Hot = Venusian
            elif ((planet.gas_mass / planet.mass) > 0.0001):
                # Accreted gas
                planet.type = PlanetType.ICE  # But no Greenhouse
                planet.ice_cover = 1.0  # or liquid water
                # Make it an Ice World
            elif (planet.surf_pressure <= 250 * millibar):  # Thin air = Martian
                planet.type = PlanetType.MARTIAN
            elif (planet.surf_temp < FREEZING_POINT_OF_WATER):
                planet.type = PlanetType.ICE
            else:
                # TODO: Implement error handling for unclassified planets.
                # If planet type remains `UNKNOWN` after classification logic,
                # raise an error or log a critical warning to identify and address
                # gaps in the classification rules.
                planet.type = PlanetType.UNKNOWN
                '''if (flag_verbose & 0x0001)
                    fprintf (stderr, "%12s\tp=%4.2Lf\tm=%4.2Lf\tg=%4.2Lf\tt=%+.1Lf\t%s\t Unknown %s\n",
                                    type_string (planet.type),
                                    planet.surf_pressure,
                                    planet.mass * SUN_MASS_IN_EARTH_MASSES,
                                    planet.surf_grav,
                                    planet.surf_temp  - EARTH_AVERAGE_KELVIN,
                                    planet_id,
                                    ((int)planet.day == (int)(planet.orb_period * 24.0) or
                                     (planet.resonant_period)) ? "(1-Face)" : ""
                             )'''

    if do_moons and not is_moon:
        for protomoon in protoplanet.moons:
            if protomoon.mass > 10 ** -6 * earth_mass:
                protomoon.orbit = planet.orbit

                # Note: adjusts density, which is used in computing the roche limit.
                moon = generate_planet(
                    protoplanet=protomoon,
                    star=star,
                    random_tilt=random_tilt,
                    do_gases=do_gases,
                    do_moons=do_moons,
                    is_moon=True,
                )

                roche_limit_r = roche_limit(planet, moon)
                hill_sphere_r = hill_sphere(planet, star)

                if roche_limit_r * 1.5 < hill_sphere_r / 2:
                    moon_a = random.uniform(
                        roche_limit_r * 1.5,
                        hill_sphere_r / 2,
                    )
                    moon_e = random.uniform(0, 0.2)
                    moon.orbit = Orbit(a=moon_a, e=moon_e)

                else:
                    # TODO: Address unstable moon orbits. If
                    # `roche_limit_r * 1.5 >= hill_sphere_r / 2`, setting orbit to a=0, e=0
                    # is not a physical solution. Consider alternative outcomes: moon is
                    # destroyed (becomes rings), ejected, or crashes into the planet.
                    # Log this event clearly.
                    moon.orbit = Orbit(a=0*km, e=0) # Representing no stable orbit found

                planet.moons.append(moon)

                if VERBOSE:
                    print(
                        "Planet %s: %s, Moon #%d %s" % (
                            planet_id,
                            mass_repr(planet.mass),
                            len(planet.moons),
                            mass_repr(moon.mass),
                        ),
                    )
                    print(
                        "Roche limit: %s (planet.radius = %s, planet.density = %s, moon.density = %s)" % (
                            quantity_repr(roche_limit_r, km),
                            quantity_repr(planet.radius, km),
                            quantity_repr(planet.density, kg/m**3),
                            quantity_repr(moon.density, kg/m**3),
                        ),
                    )
                    print(
                        "Hill Sphere: %s (planet.orbit.a = %s, planet.mass = %s, star.mass = %s)" % (
                            quantity_repr(hill_sphere_r, km),
                            quantity_repr(planet.orbit.a, km),
                            mass_repr(planet.mass),
                            mass_repr(star.mass),
                        ),
                    )
                    print(
                        "Moon orbit: a = %s, e = %f" % (
                            quantity_repr(moon.orbit.a, km),
                            moon.orbit.e
                        ),
                    )
    return planet


###
# Smoke Test
###

JINJA2_ENVIROMENT = Environment(
    loader=FileSystemLoader(
        str(Path(__file__).parent / Path('templates'))
    ),
    autoescape=select_autoescape(['html', 'xml', 'svg']),
)

if __name__ == '__main__':
    #random.seed('earth2')
    system = generate_stellar_system(random_star())

    print(system)

    # Output SVG
    # TODO: Make SVG output configurable. Add command-line flags
    # (e.g., using `argparse`) to control whether the SVG visualization is
    # generated and to specify the output path.

    max_x = 1500
    max_y = 120
    margin = 20
    inner_edge = system.innermost_planet.orbit.a * \
        (1 - system.innermost_planet.orbit.e)
    outer_edge = system.outermost_planet.orbit.a * \
        (1 + system.outermost_planet.orbit.e)
    min_log = math.floor(math.log10(dimensionless_with_units(inner_edge, au)))
    max_log = math.ceil(math.log10(dimensionless_with_units(outer_edge, au)))

    mult = max_x / (max_log - min_log)
    offset = -mult * (1.0 + min_log)
    em_scale = 5

    def transform_planet_radius(mass):
        return em_scale * dimensionless_with_units(mass, earth_mass) ** (1/3)

    def transform_orbital_distance(distance):
        return (offset+mult) + (
            math.log10(
                dimensionless_with_units(distance, au)
            ) * mult
        )

    def transform_log_au_distance(log_au_distance):
        return (offset+mult) + (log_au_distance*mult)

    JINJA2_ENVIROMENT.filters['planet_radius'] = transform_planet_radius
    JINJA2_ENVIROMENT.filters['orbital_distance'] = transform_orbital_distance
    JINJA2_ENVIROMENT.filters['log_au_distance'] = transform_log_au_distance
    JINJA2_ENVIROMENT.filters['mass_repr'] = mass_repr

    svg_path = Path(__file__).resolve().parents[2] / Path('test.svg')
    svg_template = JINJA2_ENVIROMENT.get_template('system.svg')

    svg_path.write_text(svg_template.render(**{
        'star': system,
        'progname': 'garnets',
        'progversion': '0.0.1',
        'max_x': max_x,
        'max_y': max_y,
        'margin': margin,
        'min_log': min_log,
        'max_log': max_log,
        'log_sub_ticks': list(
            map(
                lambda dx: math.log10(dx),
                range(2, 9 + 1)
            )
        )
    }))
