from math import pi

# TODO(woursler): This file should really be broken apart.

# Units of solar masses. For scale, pluto clocks in at about 10^-8.
PROTOPLANET_MASS = 10.0**-15

# Universal Constants.
GRAV_CONSTANT = 6.672E-8  # units of dyne cm2/gram2
MOLAR_GAS_CONST = 8314.41  # units: g*m2/(sec2*K*mol)

# Tunable Constants.
# TODO(woursler): Give these some meaning?
DUST_DENSITY_COEFF = 0.002
ECCENTRICITY_COEFF = 0.077
ALPHA = 5.0
B = 1.2 * 10**-5
N = 3.0
K = 50  # gas/dust ratio
J = 1.46E-19  # Used in day-length calcs (cm2/sec2 g)
# Units of Earth Masses, Below this mass, will only product asteroids.
ASTEROID_MASS_LIMIT = 0.001

DISK_ECCENTRICITY = 0.2

# Common masses and their ratios.
SOLAR_MASS_IN_GRAMS = 1.989E33  # Units of grams
SUN_MASS_IN_EARTH_MASSES = 332775.64
SUN_MASS_IN_MOON_MASSES = 27069000
SUN_MASS_IN_JUPITER_MASSES = 1047.2

# Constants relating to physical measurements on earth
CHANGE_IN_EARTH_ANG_VEL = -1.3E-15  # Units of radians/sec/year
EARTH_MASS_IN_GRAMS = 5.977E27  # Units of grams
EARTH_RADIUS = 6.378E8  # Units of cm
EARTH_DENSITY = 5.52  # Units of g/cc
KM_EARTH_RADIUS = 6378.0  # Units of km
EARTH_ACCELERATION = 980.7  # Units of cm/sec2
EARTH_AXIAL_TILT = 23.4  # Units of degrees
EARTH_EXOSPHERE_TEMP = 1273.0  # Units of degrees Kelvin
EARTH_EFFECTIVE_TEMP = 250.0  # Units of degrees Kelvin was 255
EARTH_WATER_MASS_PER_AREA = 3.83E15  # grams per square km
EARTH_CONVECTION_FACTOR = 0.43  # from Hart, eq.20
FREEZING_POINT_OF_WATER = 273.15  # Units of degrees Kelvin
EARTH_AVERAGE_CELSIUS = 14.0  # Average Earth Temperature
EARTH_AVERAGE_KELVIN = EARTH_AVERAGE_CELSIUS + FREEZING_POINT_OF_WATER
EARTH_ALBEDO = 0.3  # was .33 for a while
EARTH_SURF_PRES_IN_MILLIBARS = 1013.25
EARTH_SURF_PRES_IN_MMHG = 760
EARTH_SURF_PRES_IN_PSI = 14.696

# --- BELOW THIS LINE IS RANDOM UNITS STUFF
# TODO(woursler): natu!

RADIANS_PER_ROTATION = 2.0 * pi

# Time definitions and ratios
DAYS_IN_A_YEAR = 365.256  # Earth days per Earth year
SECONDS_PER_HOUR = 3600.0

# Distance definitions and ratios
CM_PER_AU = 1.495978707E13  # number of cm in an AU
CM_PER_KM = 1.0E5  # number of cm in a km
KM_PER_AU = CM_PER_AU / CM_PER_KM
CM_PER_METER = 100.0

# Pressure definitions and ratios
MMHG_TO_MILLIBARS = EARTH_SURF_PRES_IN_MILLIBARS / EARTH_SURF_PRES_IN_MMHG
PSI_TO_MILLIBARS = EARTH_SURF_PRES_IN_MILLIBARS / EARTH_SURF_PRES_IN_PSI
PPM_PRESSURE = EARTH_SURF_PRES_IN_MILLIBARS / 1000000.
MILLIBARS_PER_BAR = 1000.
MILLIBARS_PER_ATM = 1013.25

# --- BELOW THIS LINE IS STUFF RELATED TO ATMOSPHERIC CHEMISTRY

# Misc stuff I don't know what to make of.
GAS_RETENTION_THRESHOLD = 6.0  # ratio of esc vel to RMS vel
CLOUD_COVERAGE_FACTOR = 1.839E-8  # km^2/kg

# The rough pressure of assumed water in human respiration.
H2O_ASSUMED_PRESSURE = 47. * MMHG_TO_MILLIBARS  # Dole p. 15

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
