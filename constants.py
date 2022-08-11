from math import pi

# TODO(woursler): This file should really be broken apart.

# Units of solar masses. For scale, pluto clocks in at about 10^-8.
PROTOPLANET_MASS = 10.0**-15

# Universal Constants.
GRAV_CONSTANT = 6.672E-8  # units of dyne cm2/gram2
MOLAR_GAS_CONST = 8314.41  # units: g*m2/(sec2*K*mol)

# Tunable Constants.
# TODO(woursler): Give these some meaning?
DUST_DENSITY_COEFF = 0.002  #original value = 0.002
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


# Atomic weights of common gasses used for RMS velocity calcs
# This table is from Dole's book "Habitable Planets for Man", p. 38

ATOMIC_HYDROGEN = 1.0  # H
MOL_HYDROGEN = 2.0  # H2
HELIUM = 4.0  # He
ATOMIC_NITROGEN = 14.0  # N
ATOMIC_OXYGEN = 16.0  # O
METHANE = 16.0  # CH4
AMMONIA = 17.0  # NH3
WATER_VAPOR = 18.0  # H2O
NEON = 20.2  # Ne
MOL_NITROGEN = 28.0  # N2
CARBON_MONOXIDE = 28.0  # CO
NITRIC_OXIDE = 30.0  # NO
MOL_OXYGEN = 32.0  # O2
HYDROGEN_SULPHIDE = 34.1  # H2S
ARGON = 39.9  # Ar
CARBON_DIOXIDE = 44.0  # CO2
NITROUS_OXIDE = 44.0  # N2O
NITROGEN_DIOXIDE = 46.0  # NO2
OZONE = 48.0  # O3
SULPH_DIOXIDE = 64.1  # SO2
SULPH_TRIOXIDE = 80.1  # SO3
KRYPTON = 83.8  # Kr
XENON = 131.3  # Xe

# atomic numbers for common / relevant atoms for use in ChemTable indexes
# TODO(woursler): Migrate the whole ChemTable into something more pythonic.
AN_H = 1
AN_HE = 2
AN_N = 7
AN_O = 8
AN_F = 9
AN_NE = 10
AN_P = 15
AN_CL = 17
AN_AR = 18
AN_BR = 35
AN_KR = 36
AN_I = 53
AN_XE = 54
AN_HG = 80
AN_AT = 85
AN_RN = 86
AN_FR = 87
# "Atomic numbers" for compounds in ChemTable indexes
AN_NH3 = 900
AN_H2O = 901
AN_CO2 = 902
AN_O3 = 903
AN_CH4 = 904
AN_CH3CH2OH = 905

# Inspired partial pressure tolerances for gases in an atmosphere.
# Used to determine if the atomsphere is breathable or toxic.
# Taken from Dole p 15, 16, 18
MIN_O2_IPP = 72 * MMHG_TO_MILLIBARS
MAX_O2_IPP = 400 * MMHG_TO_MILLIBARS
MAX_HE_IPP = 61000 * MMHG_TO_MILLIBARS
MAX_NE_IPP = 3900 * MMHG_TO_MILLIBARS
MAX_N2_IPP = 2330 * MMHG_TO_MILLIBARS
MAX_AR_IPP = 1220 * MMHG_TO_MILLIBARS
MAX_KR_IPP = 350 * MMHG_TO_MILLIBARS
MAX_XE_IPP = 160 * MMHG_TO_MILLIBARS
MAX_CO2_IPP = 7 * MMHG_TO_MILLIBARS
MAX_HABITABLE_PRESSURE = 118 * PSI_TO_MILLIBARS
# The next gases are listed  in Dole
# as poisonous in parts per million by volume at 1 atm.
MAX_F_IPP = 0.1 * PPM_PRESSURE
MAX_CL_IPP = 1.0 * PPM_PRESSURE
MAX_NH3_IPP = 100 * PPM_PRESSURE
MAX_O3_IPP = 0.1 * PPM_PRESSURE
MAX_CH4_IPP = 50000 * PPM_PRESSURE

H20_ASSUMED_PRESSURE = 47. * MMHG_TO_MILLIBARS  # Dole p. 15

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
