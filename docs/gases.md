# Gases

Gases are important, both during stellar formation, and when considering the contents of planetary atomspheres.

Stargen's approach to gases is a bit haphazard, and garnets attempts to formalize it a bit, mostly by storing the data in a single CSV, rather than piecemeal in code and as constants and defines.

The following is a best effort to translate several portions of stargen code into constants usable elsewhere.

```
# Atomic weights of common gasses used for RMS velocity calculations
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
```