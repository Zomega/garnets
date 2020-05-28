"""Physical and inferred constants related to stellar system formation."""

from xatu.units import K
from xatu.units import cm
from xatu.units import deg
from xatu.units import earth_mass
from xatu.units import g
from xatu.units import kg
from xatu.units import km
from xatu.units import m
from xatu.units import mol
from xatu.units import rad
from xatu.units import s
from xatu.units import solar_mass
from xatu.units import year
from xatu.units import mmhg

# TODO(woursler): This file should really be broken apart.

# For scale, pluto clocks in at about 10^-8 solar masses.
PROTOPLANET_MASS = 10.0 ** -15 * solar_mass

# Universal Constants.
GRAV_CONSTANT = 6.67430e-11 * m ** 3 / kg / s**2
MOLAR_GAS_CONST = 8.3144598 * m ** 2 * kg / s ** 2 / K / mol

# Tunable Constants.
# TODO(woursler): Give these some meaning?
DUST_DENSITY_COEFF = 0.002
ECCENTRICITY_COEFF = 0.077
ALPHA = 5.0
B = 1.2 * 10**-5
GAS_DUST_RATIO = 50  # gas/dust ratio
J = 1.46E-19 * cm ** 2 / s ** 2 / g  # Used in day-length calcs
# Units of Earth Masses, Below this mass, will only produce asteroids.
ASTEROID_MASS_LIMIT = 0.001 * earth_mass

# Represents the typical eccentricity of particles in the
# proto-planetary disk.
DISK_ECCENTRICITY = 0.2

# Constants relating to physical measurements on earth
CHANGE_IN_EARTH_ANG_VEL = -1.3E-15 * rad / s / year
EARTH_RADIUS = 6.378E8 * cm  # Units of cm
EARTH_DENSITY = 5.52 * g / cm ** 3
EARTH_AXIAL_TILT = 23.4 * deg
EARTH_EXOSPHERE_TEMP = 1273.0 * K
EARTH_EFFECTIVE_TEMP = 250.0 * K
EARTH_WATER_MASS_PER_AREA = 3.83E15 * g / km**2
EARTH_CONVECTION_FACTOR = 0.43  # from Hart, eq.20
FREEZING_POINT_OF_WATER = 273.15 * K  # TODO(woursler): USE GAS?
EARTH_AVERAGE_TEMP = 287.15 * K
EARTH_ALBEDO = 0.3  # was .33 for a while

# --- BELOW THIS LINE IS STUFF RELATED TO ATMOSPHERIC CHEMISTRY

# Misc stuff I don't know what to make of.
GAS_RETENTION_THRESHOLD = 6.0  # ratio of esc vel to RMS vel
CLOUD_COVERAGE_FACTOR = 1.839E-8 * km ** 2 / kg

# The rough pressure of assumed water in human respiration.
H2O_ASSUMED_PRESSURE = 47. * mmhg  # Dole p. 15

# Albedo estimates
# TODO(woursler): These are not sourced.
ICE_ALBEDO = 0.7
CLOUD_ALBEDO = 0.52
GAS_GIANT_ALBEDO = 0.5
AIRLESS_ICE_ALBEDO = 0.5
GREENHOUSE_TRIGGER_ALBEDO = 0.20
ROCKY_ALBEDO = 0.15
ROCKY_AIRLESS_ALBEDO = 0.07
WATER_ALBEDO = 0.04
