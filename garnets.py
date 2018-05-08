import logging
import random
from math import sqrt
from stellar_system import Star
from stellar_system import Planetesimal
from stellar_system import Protoplanet
from stellar_system import Protomoon
from accrete import CircumstellarDisk
from constants import ECCENTRICITY_COEFF, PROTOPLANET_MASS
from constants import SUN_MASS_IN_EARTH_MASSES

logging.getLogger().setLevel(logging.INFO)


def random_star():  # TODO: Add seed?
    # Sources
    # exoplanets.co/exoplanet-correlations/host-star-mass-distribution.html
    # en.wikipedia.org/wiki/Main_sequence#mediaviewer/File:HRDiagram.png
    # TODO: Code up generation.
    age = random.randrange(1*10**9, 6*10**9)
    return Star(age=age, mass_ratio=1)


def generate_stellar_system(star, do_gases=True, do_moons=True):
    protoplanets = dist_planetary_masses(
        star, 0.0, star.stellar_dust_limit, do_moons)
    for p in protoplanets:
        print(p)
        print(generate_planet(p, star))
    flag_char = None  # TODO: Remove / replace
    system = generate_planets(star, flag_char, do_gases, do_moons)
    return system

# Create protoplanets.


def random_planetesimal(disk):
    a = random.uniform(disk.planet_inner_bound, disk.planet_outer_bound)
    e = 1.0 - (random.uniform(0.0, 1.0) ** ECCENTRICITY_COEFF)
    if e > .99:
        e = .99
    return Planetesimal(
        disk=disk,
        a=a,
        e=e,
        dust_mass=PROTOPLANET_MASS,
        gas_mass=0,
    )


def dist_planetary_masses(star, inner_dust, outer_dust, do_moons=True):
    disk = CircumstellarDisk(star)

    planets = []

    sequential_failures = 0

    while disk.dust_left and sequential_failures < 10**3:
        canidate = random_planetesimal(disk)

        iel = canidate.inner_effect_limit
        oel = canidate.outer_effect_limit

        if disk.dust_available(iel, oel) > 0:
            sequential_failures = 0
            logging.info("Injecting planetesimal at " +
                         str(canidate.a) + " AU ...")

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
    return Protoplanet(
        star=planetesimal.disk.star,
        a=planetesimal.a,
        e=planetesimal.e,
        dust_mass=planetesimal.dust_mass,
        gas_mass=planetesimal.gas_mass
    )


def convert_planetesimal_to_protomoon(planetesimal, planet):
    print("Capturing a protomoon.")
    return Protomoon(
        protoplanet=planet,
        a=None,
        e=None,
        dust_mass=planetesimal.dust_mass,
        gas_mass=planetesimal.gas_mass,
    )


def coalesce_planetesimals(disk, planets, canidate, do_moons):
    finished = False

    # First we try to find an existing planet with an over-lapping orbit.
    for planet in planets:
        print("Out of order", planet, canidate)

        diff = planet.a - canidate.a

        if diff > 0.0:
            dist1 = (canidate.a * (1.0 + canidate.e) *
                     (1.0 + canidate.reduced_mass)) - canidate.a
            # x aphelion
            dist2 = planet.a - (planet.a * (1.0 - planet.e)
                                * (1.0 - planet.reduced_mass))
        else:
            dist1 = (
                canidate.a -
                (canidate.a * (1.0 - canidate.e) * (1.0 - canidate.reduced_mass)
            ))
            # x perihelion
            dist2 = (planet.a * (1.0 + planet.e) *
                     (1.0 + planet.reduced_mass)) - planet.a

        if abs(diff) <= abs(dist1) or abs(diff) <= abs(dist2):
            # Figure out the new orbit.
            a = (planet.mass + canidate.mass) / \
                ((planet.mass / planet.a) + (canidate.mass / canidate.a))

            temp = planet.mass * sqrt(planet.a) * sqrt(1.0 - (planet.e ** 2.0))
            temp = temp + (canidate.mass * sqrt(canidate.a) *
                           sqrt(sqrt(1.0 - (canidate.e ** 2.0))))
            temp = temp / ((planet.mass + canidate.mass) * sqrt(canidate.a))
            temp = 1.0 - (temp ** 2.0)
            if temp < 0.0 or temp >= 1.0:
                temp = 0.0
            e = sqrt(temp)

            if do_moons:
                if canidate.mass < canidate.critical_mass:
                    if canidate.mass * SUN_MASS_IN_EARTH_MASSES < 2.5 \
                        and canidate.mass * SUN_MASS_IN_EARTH_MASSES > .0001 \
                        and planet.mass_of_moons < planet.mass * .05 \
                        and planet.mass > canidate.mass:
                        # TODO: Remove planet.mass > canidate.mass distinction, just switch the canidate and planet!
                        planet.add_moon(
                            convert_planetesimal_to_protomoon(canidate, planet))
                        logging.info("Moon captured at " + str(planet.a) + " AU. Planet Mass: " + str(planet.mass * SUN_MASS_IN_EARTH_MASSES) +
                                     " earth masses; Moon Mass: " + str(canidate.mass * SUN_MASS_IN_EARTH_MASSES) + " earth masses.")
                        finished = True
                        break
                    else:
                        # TODO: Reasons.
                        logging.info("Did not capture potential moon at " +
                                     str(planet.a) + " AU. Collision imminent.")

            logging.info(
                "Collision between two planetesimals! Computing new orbit and accumulating additional mass.")
            # Accrete MORE DUST! TODO: Refactor to this.
            disk.accrete_dust(planet)

            planet.a = a
            planet.e = e
            planet.dust_mass = planet.dust_mass + canidate.dust_mass  # + new_dust
            planet.gas_mass = planet.gas_mass + canidate.gas_mass  # + new_gas
            finished = True
            logging.info(
                "Conglomerate is now " +
                str(planet.mass * SUN_MASS_IN_EARTH_MASSES) +
                " earth masses at " + str(planet.a) + " AU."
            )

    if not finished:
        # TODO: Extra info.
        logging.info("New Protoplanet at " + str(canidate.a) + "AU.")
        planets.append(convert_planetesimal_to_protoplanet(canidate))


def generate_planet(protoplanent, sun, random_tilt=0, planet_id=None, do_gases=True, do_moons=True, is_moon=False):
    logging.warning("generate_planet( ... ) not implemented yet.")  # TODO
    return

def generate_planets(star, flag_char, do_gasses, do_moons):
    logging.warning("generate_planets( ... ) not implemented yet.")  # TODO
    return


###
# Smoke Test
###

generate_stellar_system(random_star())
