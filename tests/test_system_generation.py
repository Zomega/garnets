"""Unit and integration tests for stellar system generation."""

import math
import random
import pytest

from xatu.core import dimensionless_with_units, quantity_repr, UNITLESS_UNIT
from xatu.units import (
    K, atm, au, bar, cm, deg, earth_mass, g, g_force, hour,
    jupiter_mass, kg, km, lunar_mass, m, mol, neptune_mass, rad, s,
    solar_mass, year,
)

from accrete import CircumstellarDisk, CircumstellarDustLane
from chemtable import GASES, lookup_gas
from constants import (
    EARTH_DENSITY, EARTH_RADIUS, PROTOPLANET_MASS, FREEZING_POINT_OF_WATER,
)
from enviroment import (
    BreathabilityPhrase, PlanetType, Zone,
    acceleration, boiling_point, cloud_fraction, day_length,
    empirical_density, escape_vel, est_temp, gas_life, grnhouse,
    hydro_fraction, ice_fraction, inclination, iterate_surface_temp,
    kothari_radius, min_molec_weight, orb_zone, period, pressure,
    rms_vel, vol_inventory, volume_density, volume_radius,
)
from garnets import (
    generate_planet, generate_stellar_system, random_star, random_planetesimal,
)
from stellar_system import Orbit, Planet, Planetoid, Protoplanet, Star, mass_repr


def test_chemtable_lookup():
    """Verify gas lookup by symbol and standard gases exist."""
    h2 = lookup_gas("H2")
    assert h2.symbol == "H2"
    assert h2.num == 910
    n2 = lookup_gas("N2")
    assert n2.symbol == "N2"
    assert len(GASES) > 10

    with pytest.raises(NotImplementedError):
        lookup_gas("Unobtainium")


def test_mass_repr():
    """Verify mass_repr produces expected formatted strings across scales."""
    assert "lunar_mass" in mass_repr(1.0 * lunar_mass)
    assert "earth_mass" in mass_repr(2.0 * earth_mass)
    assert "neptune_mass" in mass_repr(5.0 * neptune_mass)
    assert "jupiter_mass" in mass_repr(10.0 * jupiter_mass)
    assert "solar_mass" in mass_repr(100.0 * jupiter_mass)


def test_orbit_properties():
    """Verify periapsis and apoapsis calculations."""
    orbit = Orbit(a=2.0 * au, e=0.1)
    assert abs(dimensionless_with_units(orbit.periapsis, au) - 1.8) < 1e-6
    assert abs(dimensionless_with_units(orbit.apoapsis, au) - 2.2) < 1e-6


def test_circumstellar_disk_dust_availability():
    """Verify dust lane splitting and dust availability checks."""
    star = Star(age=4.5e9 * year, mass_ratio=1.0)
    disk = CircumstellarDisk(star)
    assert disk.dust_left is True
    assert disk.dust_available(0.1 * au, 10.0 * au) is True
    assert disk.dust_available(250.0 * au, 300.0 * au) is False


def test_planetoid_effect_limits():
    """Verify gravitational sweep limits scale with mass and orbit."""
    p1 = Planetoid(orbit=Orbit(a=1.0 * au, e=0.0), dust_mass=PROTOPLANET_MASS, gas_mass=0 * kg)
    iel = dimensionless_with_units(p1.inner_effect_limit, au)
    oel = dimensionless_with_units(p1.outer_effect_limit, au)
    assert iel < 1.0
    assert oel > 1.0


def test_physical_environment_calculations():
    """Verify standard planetary formulas calculate sane physical quantities."""
    mass = 1.0 * earth_mass
    r = 6378.0 * km
    g_acc = acceleration(mass, r)
    assert abs(dimensionless_with_units(g_acc, g_force) - 1.0) < 0.05

    v_esc = escape_vel(mass, r)
    assert abs(dimensionless_with_units(v_esc, km / s) - 11.2) < 0.5

    v_rms = rms_vel(28.0 * g / mol, 300.0 * K)
    assert dimensionless_with_units(v_rms, m / s) > 0

    p_boil = boiling_point(1.0 * atm)
    assert abs(dimensionless_with_units(p_boil, K) - 373.15) < 10.0

    p_zero_boil = boiling_point(0.0 * atm)
    assert dimensionless_with_units(p_zero_boil, K) == 0.0

    hydro = hydro_fraction(1000.0, r)
    assert 0.0 <= hydro <= 1.0

    clouds = cloud_fraction(288.0 * K, 2.0 * g / mol, r, hydro)
    assert 0.0 <= clouds <= 1.0

    ice = ice_fraction(hydro, 250.0 * K)
    assert 0.0 <= ice <= 1.0


@pytest.mark.parametrize("seed", [42, 12345, 999999, 2026])
def test_full_system_generation_seeds(seed):
    """Smoketest multi-seed complete generation to ensure no crashes."""
    random.seed(seed)
    star = Star(age=random.randrange(1 * 10**9, 6 * 10**9) * year, mass_ratio=1.0)
    system = generate_stellar_system(star, do_gases=True, do_moons=True)
    assert system is not None
    assert isinstance(system.planets, list)
    for p in system.planets:
        assert p.mass > 0 * kg
        assert p.radius > 0 * km
        assert p.type != PlanetType.UNKNOWN
        # repr shouldn't raise UnitsError
        p_repr = repr(p)
        assert len(p_repr) > 0
    sys_repr = repr(system)
    assert len(sys_repr) > 0
