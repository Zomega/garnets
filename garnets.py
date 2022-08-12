import numpy as np
import logging
import random
from math import sqrt, log
from stellar_system import Star
from stellar_system import Planetesimal
from stellar_system import Protoplanet
from stellar_system import Protomoon
from stellar_system import Planet
from stellar_system import Orbit
from accrete import CircumstellarDisk
from constants import ECCENTRICITY_COEFF, PROTOPLANET_MASS
from constants import SUN_MASS_IN_EARTH_MASSES
from constants import EARTH_ALBEDO, GAS_GIANT_ALBEDO, FREEZING_POINT_OF_WATER, KM_PER_AU, EARTH_AVERAGE_KELVIN, EARTH_EXOSPHERE_TEMP
from constants import MOL_NITROGEN, MOL_HYDROGEN, HELIUM
from constants import ASTEROID_MASS_LIMIT
from constants import MILLIBARS_PER_BAR

from enviroment import kothari_radius, gas_life, rms_vel, est_temp, period, day_length, acceleration, gravity, min_molec_weight, orb_zone, volume_radius, volume_density, grnhouse, boiling_point, escape_vel, empirical_density, inclination, iterate_surface_temp, pressure, vol_inventory
from enviroment import PlanetType

from math import exp
from math import inf as INCREDIBLY_LARGE_NUMBER  # TODO(woursler): Just use inf

from util import about, random_number, random_eccentricity

from chemtable import gases

logging.getLogger().setLevel(logging.INFO)


def random_star():  # TODO: Add seed?
    # Sources
    # exoplanets.co/exoplanet-correlations/host-star-mass-distribution.html
    # en.wikipedia.org/wiki/Main_sequence#mediaviewer/File:HRDiagram.png
    # TODO: Code up generation.
    age = random.randrange(1*10**9, 6*10**9)
    return Star(age=age, mass_ratio=1)


def generate_stellar_system(star, do_gases=True, do_moons=True):
    protoplanets = generate_planetary_masses(
        star,
        0.0,
        star.stellar_dust_limit,
        do_moons=do_moons
    )
    star.planets = [
        generate_planet(
            p,
            star,
            do_gases=do_gases,
            do_moons=do_moons
        ) for p in protoplanets
    ]
    return star

# Create protoplanets.


def random_planetesimal(disk):
    a = random.uniform(disk.planet_inner_bound, disk.planet_outer_bound)
    e = 1.0 - (random.uniform(0.0, 1.0) ** ECCENTRICITY_COEFF)
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
            logging.info("Injecting planetesimal at " +
                         str(canidate.orbit.a) + " AU ...")

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
        orbit=planetesimal.orbit,
        dust_mass=planetesimal.dust_mass,
        gas_mass=planetesimal.gas_mass
    )


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

        if diff > 0.0:
            dist1 = canidate.orbit.apoapsis * (1.0 + canidate.reduced_mass) - canidate.orbit.a
            # x aphelion
            dist2 = planet.orbit.a - (planet.orbit.periapsis * (1.0 - planet.reduced_mass))
        else:
            dist1 = canidate.orbit.a - (canidate.orbit.periapsis * (1.0 - canidate.reduced_mass))
            # x perihelion
            dist2 = (planet.orbit.apoapsis * (1.0 + planet.reduced_mass)) - planet.orbit.a

        if abs(diff) <= abs(dist1) or abs(diff) <= abs(dist2):
            # Figure out the new orbit.
            a = (planet.mass + canidate.mass) / \
                ((planet.mass / planet.orbit.a) + (canidate.mass / canidate.orbit.a))

            temp = planet.mass * sqrt(planet.orbit.a) * sqrt(1.0 - (planet.orbit.e ** 2.0))
            temp = temp + (canidate.mass * sqrt(canidate.orbit.a) *
                           sqrt(sqrt(1.0 - (canidate.orbit.e ** 2.0))))
            temp = temp / ((planet.mass + canidate.mass) * sqrt(canidate.orbit.a))
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
                        logging.info("Moon captured at " + str(planet.orbit.a) + " AU. Planet Mass: " + str(planet.mass * SUN_MASS_IN_EARTH_MASSES) +
                                     " earth masses Moon Mass: " + str(canidate.mass * SUN_MASS_IN_EARTH_MASSES) + " earth masses.")
                        finished = True
                        break
                    else:
                        # TODO: Reasons.
                        logging.info("Did not capture potential moon at " +
                                     str(planet.orbit.a) + " AU. Collision imminent.")

            logging.info(
                "Collision between two planetesimals! Computing new orbit and accumulating additional mass.")
            # Accrete MORE DUST! TODO: Refactor to this.
            disk.accrete_dust(planet)

            planet.orbit = Orbit(a=a, e=e)
            #####
            planet.orbit_a = a
            planet.orbit_e = e
            planet.dust_mass = planet.dust_mass + canidate.dust_mass  # + new_dust
            planet.gas_mass = planet.gas_mass + canidate.gas_mass  # + new_gas
            finished = True
            logging.info(
                "Conglomerate is now " +
                str(planet.mass * SUN_MASS_IN_EARTH_MASSES) +
                " earth masses at " + str(planet.orbit.a) + " AU."
            )

    if not finished:
        # TODO: Extra info.
        logging.info("New Protoplanet at " + str(canidate.orbit.a) + "AU.")
        planets.append(convert_planetesimal_to_protoplanet(canidate))


def calculate_gases(star, planet, planet_id):
    if planet.surf_pressure > 0:

        amount = [0 for _ in range(len(gases))]
        totamount = 0
        pressure = planet.surf_pressure/MILLIBARS_PER_BAR
        n = 0

        for i in range(len(gases)):

            yp = gases[i].boil / \
                (373. * ((log((pressure) + 0.001) / -5050.5) + (1.0 / 373.)))

            if ((yp >= 0 and yp < planet.low_temp) and (gases[i].weight >= planet.molec_weight)):

                vrms = rms_vel(gases[i].weight, planet.exospheric_temp)
                pvrms = pow(1 / (1 + vrms / planet.esc_velocity),
                            star.age / 1e9)
                abund = gases[i].abunds                 # gases[i].abunde
                react = 1.0
                fract = 1.0
                pres2 = 1.0

                if gases[i].symbol == "Ar":
                    react = .15 * star.age/4e9

                elif gases[i].symbol == "He":

                    abund = abund * (0.001 + (planet.gas_mass / planet.mass))
                    pres2 = (0.75 + pressure)
                    react = pow(1 / (1 + gases[i].reactivity),
                                star.age/2e9 * pres2)

                elif (gases[i].symbol == "O" or gases[i].symbol == "O2") and star.age > 2e9 and planet.surf_temp > 270 and planet.surf_temp < 400:
                    pres2 = (0.89 + pressure/4)
                    react = pow(
                        1 / (1 + gases[i].reactivity), pow(star.age/2e9, 0.25) * pres2)

                elif gases[i].symbol == "CO2" and star.age > 2e9 and planet.surf_temp > 270 and planet.surf_temp < 400:
                    pres2 = (0.75 + pressure)
                    react = pow(
                        1 / (1 + gases[i].reactivity), pow(star.age/2e9, 0.5) * pres2)
                    react *= 1.5

                else:
                    pres2 = 0.75 + pressure
                    react = pow(
                        1 / (1 + gases[i].reactivity), star.age/2e9 * pres2)

                fract = (1 - (planet.molec_weight / gases[i].weight))

                amount[i] = abund * pvrms * react * fract

                '''if ((flag_verbose & 0x4000) and
                    (strcmp(gases[i].symbol, "O") == 0 or
                     strcmp(gases[i].symbol, "N") == 0 or
                     strcmp(gases[i].symbol, "Ar") == 0 or
                     strcmp(gases[i].symbol, "He") == 0 or
                     strcmp(gases[i].symbol, "CO2") == 0))

                    fprintf (stderr, "%-5.2Lf %-3.3s, %-5.2Lf = a %-5.2Lf * p %-5.2Lf * r %-5.2Lf * p2 %-5.2Lf * f %-5.2Lf\t(%.3Lf%%)\n",
                              planet.mass * SUN_MASS_IN_EARTH_MASSES,
                              gases[i].symbol,
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

            for i in range(len(gases)):

                if amount[i] > 0.0:

                    planet.atmosphere.append((gases[i], planet.surf_pressure * amount[i] / totamount))

                    '''if (flag_verbose & 0x2000)

                        if ((planet.atmosphere[n].num == AN_O) and
                            inspired_partial_pressure (planet.surf_pressure,
                                                       planet.atmosphere[n].surf_pressure)
                            > gases[i].max_ipp)

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
    return 2.44 * planet.radius * pow((planet.density / moon.density), (1.0 / 3.0))

def hill_sphere(planet, star):
    return planet.orbit.a * KM_PER_AU * pow((planet.mass / (3.0 * star.mass_ratio)), (1.0 / 3.0))

def generate_planet(protoplanet, star, random_tilt=0, planet_id=None, do_gases=True, do_moons=True, is_moon=False):
    planet = Planet(
        sun=star,
        orbit=protoplanet.orbit,
        dust_mass=protoplanet.dust_mass,
        gas_mass=protoplanet.gas_mass,
        mass=protoplanet.mass,
        axial_tilt=inclination(protoplanet.orbit.a) if random_tilt else 0,
        atmosphere=None,
        surf_temp=0,
        high_temp=0,
        low_temp=0,
        max_temp=0,
        min_temp=0,
        greenhs_rise=0,
        resonant_period=False,
        orbit_zone=orb_zone(star.luminosity_ratio,  protoplanet.orbit.a),
        orb_period=period(protoplanet.orbit.a,  protoplanet.mass, star.mass_ratio)
    )

    planet.exospheric_temp = EARTH_EXOSPHERE_TEMP / \
        ((planet.orbit.a / star.r_ecosphere) ** 2)
    planet.rms_velocity = rms_vel(MOL_NITROGEN, planet.exospheric_temp)
    planet.core_radius = kothari_radius(
        planet.dust_mass, False, planet.orbit_zone)

    # Calculate the radius as a gas giant, to verify it will retain gas.
    # Then if mass > Earth, it's at least 5% gas and retains He, it's
    # some flavor of gas giant.

    planet.density = empirical_density(
        planet.mass, planet.orbit.a, star.r_ecosphere, True)
    planet.radius = volume_radius(planet.mass, planet.density)

    planet.surf_accel = acceleration(planet.mass, planet.radius)
    planet.surf_grav = gravity(planet.surf_accel)

    planet.molec_weight = min_molec_weight(planet)

    if (((planet.mass * SUN_MASS_IN_EARTH_MASSES) > 1.0)
        and ((planet.gas_mass / planet.mass) > 0.05)
            and (min_molec_weight(planet) <= 4.0)):

        if ((planet.gas_mass / planet.mass) < 0.20):
            planet.type = PlanetType.SUB_SUB_GAS_GIANT
        elif ((planet.mass * SUN_MASS_IN_EARTH_MASSES) < 20.0):
            planet.type = PlanetType.SUB_GAS_GIANT
        else:
            planet.type = PlanetType.GAS_GIANT

    else:  # If not, it's rocky.

        planet.radius = kothari_radius(planet.mass, False, planet.orbit_zone)
        planet.density = volume_density(planet.mass, planet.radius)

        planet.surf_accel = acceleration(planet.mass, planet.radius)
        planet.surf_grav = gravity(planet.surf_accel)

        if ((planet.gas_mass / planet.mass) > 0.000001):

            h2_mass = planet.gas_mass * 0.85
            he_mass = (planet.gas_mass - h2_mass) * 0.999

            h2_loss = 0.0
            he_loss = 0.0

            h2_life = gas_life(MOL_HYDROGEN, planet)
            he_life = gas_life(HELIUM, planet)

            if (h2_life < star.age):
                #math.exp with a value above 709 results in a math range error
                #this is a dumb fix. STH 2021-0131
                #h2_loss = ((1.0 - (1.0 / np.exp(star.age / h2_life))) * h2_mass)
                if (star.age / h2_life)>709:
                    h2_loss = ((1.0 - (1.0 / exp(709.0))) * h2_mass)
                else:
                    h2_loss = ((1.0 - (1.0 / exp(star.age / h2_life))) * h2_mass)

                planet.gas_mass -= h2_loss
                planet.mass -= h2_loss

                planet.surf_accel = acceleration(planet.mass, planet.radius)
                planet.surf_grav = gravity(planet.surf_accel)

            if (he_life < star.age) and (he_life < 0.00001):
                he_loss = 1.0
            else:
                print("LOOK AT ME: Star Age = {0:4.1f} Gyr, He life = {1:6.6f}, He mass = {2:6.6f}".format(star.age/1e9, he_life, he_mass))
                he_loss = ((1.0 - (1.0 / np.exp(star.age / he_life))) * he_mass)

                planet.gas_mass -= he_loss
                planet.mass -= he_loss

                planet.surf_accel = acceleration(planet.mass, planet.radius)
                planet.surf_grav = gravity(planet.surf_accel)

            '''if (((h2_loss + he_loss) > .000001) and (flag_verbose & 0x0080)):
                fprintf(stderr, "%s\tLosing gas: H2: %5.3Lf EM, He: %5.3Lf EM\n",
                        planet_id,
                        h2_loss * SUN_MASS_IN_EARTH_MASSES, he_loss * SUN_MASS_IN_EARTH_MASSES)'''

    planet.day = day_length(planet)    # Modifies planet.resonant_period
    planet.esc_velocity = escape_vel(planet.mass, planet.radius)

    # Environmental conditions for gas giant planets
    if planet.type == PlanetType.GAS_GIANT or planet.type == PlanetType.SUB_GAS_GIANT or planet.type == PlanetType.SUB_SUB_GAS_GIANT:

        planet.greenhouse_effect = False
        planet.volatile_gas_inventory = INCREDIBLY_LARGE_NUMBER
        planet.surf_pressure = INCREDIBLY_LARGE_NUMBER

        planet.boil_point = INCREDIBLY_LARGE_NUMBER

        planet.surf_temp = INCREDIBLY_LARGE_NUMBER
        planet.greenhs_rise = 0
        planet.albedo = about(GAS_GIANT_ALBEDO, 0.1)
        planet.hydrosphere = 1.0
        planet.cloud_cover = 1.0
        planet.ice_cover = 0.0
        planet.surf_grav = gravity(planet.surf_accel)
        planet.molec_weight = min_molec_weight(planet)
        planet.surf_grav = INCREDIBLY_LARGE_NUMBER
        planet.estimated_temp = est_temp(
            star.r_ecosphere, planet.orbit.a,  planet.albedo)
        planet.estimated_terr_temp = est_temp(
            star.r_ecosphere, planet.orbit.a,  EARTH_ALBEDO)

        temp = planet.estimated_terr_temp

        if (temp >= FREEZING_POINT_OF_WATER) and (temp <= EARTH_AVERAGE_KELVIN + 10.) and (star.age > 2.0E9):
            pass
            '''if (flag_verbose & 0x8000):

                fprintf (stderr, "%s\t%s (%4.2LfEM %5.3Lf By)%s with earth-like temperature (%.1Lf C, %.1Lf F, %+.1Lf C Earth).\n",
                         planet_id,
                         planet.type == PlanetType.GAS_GIANT ? "Jovian" :
                         planet.type == PlanetType.SUB_GAS_GIANT ? "Sub-Jovian" :
                         planet.type == PlanetType.SUB_SUB_GAS_GIANT ? "Gas Dwarf" :
                         "Big",
                         planet.mass * SUN_MASS_IN_EARTH_MASSES,
                         star.age /1.0E9,
                         planet.first_moon == NULL ? "" : " WITH MOON",
                         temp - FREEZING_POINT_OF_WATER,
                         32 + ((temp - FREEZING_POINT_OF_WATER) * 1.8),
                         temp - EARTH_AVERAGE_KELVIN)'''

    else:

        planet.estimated_temp = est_temp(
            star.r_ecosphere, planet.orbit.a,  EARTH_ALBEDO)
        planet.estimated_terr_temp = est_temp(
            star.r_ecosphere, planet.orbit.a,  EARTH_ALBEDO)

        planet.surf_grav = gravity(planet.surf_accel)
        planet.molec_weight = min_molec_weight(planet)

        planet.greenhouse_effect = grnhouse(star.r_ecosphere, planet.orbit.a)
        planet.volatile_gas_inventory = vol_inventory(planet.mass,
                                                      planet.esc_velocity,
                                                      planet.rms_velocity,
                                                      star.mass_ratio,
                                                      planet.orbit_zone,
                                                      planet.greenhouse_effect,
                                                      (planet.gas_mass
                                                       / planet.mass) > 0.000001)
        planet.surf_pressure = pressure(planet.volatile_gas_inventory,
                                        planet.radius,
                                        planet.surf_grav)

        if ((planet.surf_pressure == 0.0)):
            planet.boil_point = 0.0
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

        if (do_gases and (planet.max_temp >= FREEZING_POINT_OF_WATER) and (planet.min_temp <= planet.boil_point)):
            calculate_gases(star, planet, planet_id)

        # Next we assign a type to the planet.

        if (planet.surf_pressure < 1.0):

            if (not is_moon) and ((planet.mass * SUN_MASS_IN_EARTH_MASSES) < ASTEROID_MASS_LIMIT):
                planet.type = PlanetType.ASTEROIDS
            else:
                planet.type = PlanetType.ROCK

        elif (planet.surf_pressure > 6000.0) and (planet.molec_weight <= 2.0):    # Retains Hydrogen

            planet.type = PlanetType.SUB_SUB_GAS_GIANT
            planet.gases = 0
            planet.atmosphere = None

        else:
                                                # Atmospheres:
            if (int(planet.day) == int(planet.orb_period * 24.0)) or planet.resonant_period:
                planet.type = PlanetType.ONE_FACE
            elif (planet.hydrosphere >= 0.95):
                planet.type = PlanetType.WATER                # >95% water
            elif (planet.ice_cover >= 0.95):
                planet.type = PlanetType.ICE                # >95% ice
            elif (planet.hydrosphere > 0.05):
                planet.type = PlanetType.TERRESTRIAL        # Terrestrial
                # else <5% water
            elif (planet.max_temp > planet.boil_point):
                planet.type = PlanetType.VENUSIAN            # Hot = Venusian
            elif ((planet.gas_mass / planet.mass) > 0.0001):
                                                    # Accreted gas
                planet.type = PlanetType.ICE                # But no Greenhouse
                planet.ice_cover = 1.0            # or liquid water
                # Make it an Ice World
            elif (planet.surf_pressure <= 250.0):  # Thin air = Martian
                planet.type = PlanetType.MARTIAN
            elif (planet.surf_temp < FREEZING_POINT_OF_WATER):
                planet.type = PlanetType.ICE
            else:
                planet.type = PlanetType.UNKNOWN  # TODO(woursler): Consider throwing an error here.

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
            if protomoon.mass * SUN_MASS_IN_EARTH_MASSES > .000001:
                protomoon.orbit = planet.orbit

                # Note: adjusts density, which is used in computing the roche limit.
                moon = generate_planet(
                    protoplanet=protomoon,
                    star=star,
                    random_tilt=random_tilt,
                    do_gases=do_gases,
                    do_moons=do_moons,
                    is_moon=True
                )

                # TODO(woursler): these should be their own subroutines.
                roche_limit_r = roche_limit(planet, moon)
                hill_sphere_r = hill_sphere(planet, star)

                if (roche_limit_r * 3.0) < hill_sphere_r:
                    moon_a = random_number(
                        roche_limit_r * 1.5, hill_sphere_r / 2.0) / KM_PER_AU
                    moon_e = random_eccentricity()
                    moon.orbit = Orbit(a=moon_a, e=moon_e)

                else:
                    moon.orbit = Orbit(a=0, e=0)

                planet.moons.append(moon)

                '''
                if (flag_verbose & 0x40000):

                    fprintf (stderr,
                                "   Roche limit: R = %4.2Lg, rM = %4.2Lg, rm = %4.2Lg . %.0Lf km\n"
                                "   Hill Sphere: a = %4.2Lg, m = %4.2Lg, M = %4.2Lg . %.0Lf km\n"
                                "%s Moon orbit: a = %.0Lf km, e = %.0Lg\n",
                                planet.radius, planet.density, ptr.density,
                                roche_limit,
                                planet.orbit.a * KM_PER_AU, planet.mass * SOLAR_MASS_IN_KILOGRAMS, star.mass_ratio * SOLAR_MASS_IN_KILOGRAMS,
                                hill_sphere,
                                moon_id,
                                ptr.moon_a * KM_PER_AU, ptr.moon_e
                            )


                if (flag_verbose & 0x1000):

                    fprintf (stderr, "  %s: (%7.2LfEM) %d %4.2LgEM\n",
                        planet_id,
                        planet.mass * SUN_MASS_IN_EARTH_MASSES,
                        n,
                        ptr.mass * SUN_MASS_IN_EARTH_MASSES)'''
    return planet


###
# Smoke Test
###
if __name__ == '__main__':
    random.seed('earth')
    print(generate_stellar_system(random_star()))
