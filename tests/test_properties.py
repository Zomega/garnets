"""Property-based invariant tests and physical conservation laws for garnets."""

import math
import random
from hypothesis import given, settings, strategies as st
import pytest

from xatu.core import dimensionless_with_units, UNITLESS_UNIT
from xatu.units import (
    K, atm, au, cm, deg, earth_mass, g, g_force, hour,
    jupiter_mass, kg, km, lunar_mass, m, mol, neptune_mass, rad, s,
    solar_mass, year,
)

from accrete import CircumstellarDisk, CircumstellarDustLane
from chemtable import lookup_gas
from constants import (
    EARTH_DENSITY, EARTH_RADIUS, PROTOPLANET_MASS, FREEZING_POINT_OF_WATER,
)
from enviroment import (
    BreathabilityPhrase, PlanetType, Zone,
    acceleration, boiling_point, breathability, cloud_fraction, day_length,
    empirical_density, escape_vel, est_temp, gas_life, grnhouse,
    hydro_fraction, ice_fraction, inclination, kothari_radius, min_molec_weight,
    orb_zone, period, pressure, rms_vel, vol_inventory, volume_density, volume_radius,
)
from garnets import generate_stellar_system
from stellar_system import Orbit, Planet, Planetoid, Star


@given(
    mass=st.floats(min_value=0.01, max_value=100.0),
    radius=st.floats(min_value=1000.0, max_value=100000.0),
)
@settings(max_examples=50)
def test_density_volume_mass_invariants(mass, radius):
    """Test mass = volume * density and inverse volume_radius invariants."""
    m_qty = mass * earth_mass
    r_qty = radius * km
    density = volume_density(m_qty, r_qty)
    assert dimensionless_with_units(density, g / cm**3) > 0

    reconstructed_radius = volume_radius(m_qty, density)
    r_diff = abs(
        dimensionless_with_units(reconstructed_radius - r_qty, km)
    )
    assert r_diff / radius < 1e-4


@given(
    a=st.floats(min_value=0.1, max_value=50.0),
    e=st.floats(min_value=0.0, max_value=0.8),
)
@settings(max_examples=50)
def test_orbit_periapsis_apoapsis_invariants(a, e):
    """Periapsis and apoapsis must bracket semi-major axis symmetrically."""
    orbit = Orbit(a=a * au, e=e)
    peri = dimensionless_with_units(orbit.periapsis, au)
    apo = dimensionless_with_units(orbit.apoapsis, au)

    assert peri <= a + 1e-12
    assert a <= apo + 1e-12
    assert abs((peri + apo) / 2.0 - a) < 1e-6


@given(
    separation=st.floats(min_value=0.1, max_value=40.0),
    star_mass=st.floats(min_value=0.2, max_value=3.0),
)
@settings(max_examples=30)
def test_keplers_third_law_scaling(separation, star_mass):
    """Orbital period squared should scale with semi-major axis cubed."""
    p1 = dimensionless_with_units(
        period(separation * au, 1.0 * earth_mass, star_mass * solar_mass),
        year,
    )
    p2 = dimensionless_with_units(
        period(2.0 * separation * au, 1.0 * earth_mass, star_mass * solar_mass),
        year,
    )
    # T2 / T1 == (2)^(3/2) = sqrt(8) ~ 2.828427
    ratio = p2 / p1
    assert abs(ratio - math.sqrt(8.0)) < 0.01


@given(
    seed=st.integers(min_value=1, max_value=100000),
    stellar_mass=st.floats(min_value=0.6, max_value=1.5),
)
@settings(max_examples=10, deadline=None)
def test_mass_conservation_and_physical_bounds(seed, stellar_mass):
    """Planet formation must not produce negative masses or unphysical orbits."""
    random.seed(seed)
    star = Star(age=4.5e9 * year, mass_ratio=stellar_mass)
    system = generate_stellar_system(star, do_gases=True, do_moons=True)

    total_planetary_mass = 0.0 * kg
    for p in system.planets:
        assert dimensionless_with_units(p.mass, kg) > 0
        assert dimensionless_with_units(p.dust_mass, kg) >= 0
        assert dimensionless_with_units(p.gas_mass, kg) >= 0
        # Planet mass is strictly dust + gas
        diff = abs(dimensionless_with_units(p.mass - (p.dust_mass + p.gas_mass), kg))
        assert diff < 1e-3

        # Orbit must be bounded
        assert dimensionless_with_units(p.orbit.a, au) > 0
        assert 0.0 <= p.orbit.e < 1.0

        # Physical surface parameters
        assert dimensionless_with_units(p.radius, km) > 0
        assert dimensionless_with_units(p.surf_grav, g_force) > 0
        assert 0.0 <= p.hydrosphere <= 1.0
        assert 0.0 <= p.cloud_cover <= 1.0
        assert 0.0 <= p.ice_cover <= 1.0
        assert 0.0 <= p.albedo <= 1.0

        # Breathability check runs without exception
        b = breathability(p)
        assert isinstance(b, BreathabilityPhrase)

        for moon in p.moons:
            assert dimensionless_with_units(moon.mass, kg) > 0
            assert dimensionless_with_units(moon.orbit.a, au) >= 0
            total_planetary_mass += moon.mass

        total_planetary_mass += p.mass

    # Total planetary mass formed around a solar-mass star cannot exceed circumstellar disk capacity (< 0.1 M_sun)
    assert total_planetary_mass < 0.1 * star.mass
