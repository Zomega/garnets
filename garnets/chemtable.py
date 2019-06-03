from attr import attrib
from attr import attrs
from constants import AN_AR
from constants import AN_CH4
from constants import AN_CO2
from constants import AN_H
from constants import AN_H2O
from constants import AN_HE
from constants import AN_KR
from constants import AN_N
from constants import AN_NE
from constants import AN_NH3
from constants import AN_O
from constants import AN_O3
from constants import AN_XE
from constants import MAX_AR_IPP
from constants import MAX_CH4_IPP
from constants import MAX_CO2_IPP
from constants import MAX_HE_IPP
from constants import MAX_KR_IPP
from constants import MAX_N2_IPP
from constants import MAX_NE_IPP
from constants import MAX_NH3_IPP
from constants import MAX_O2_IPP
from constants import MAX_O3_IPP
from constants import MAX_XE_IPP

# This module is used for figuring out atmospheric chemistry, but it leaves
# some things to be desired. In particular, as coded, it does not really
# consider thick / thin atmospheres very well and does not consider reactions,
# either amoung gases in an atmosphere, or with regards to fixing in the crust.

@attrs
class Gas():
    num = attrib()  # int
    symbol = attrib()  # string
    html_symbol = attrib()  # string
    name = attrib()  # Name
    weight = attrib()  # long double

    # TODO(woursler): Should use a phase diagram -- these melting and boiling points are really simplistic given the range of pressures things happen at.
    melt = attrib()  # long double
    boil = attrib()  # long double
    density = attrib()  # long double

    # These somehow measure relative abundance, but I can't work out the difference from context.
    abunde = attrib()  # long double
    abunds = attrib()  # long double

    reactivity = attrib()  # long double
    max_ipp = attrib()  # long double


gases = [
    #    A.N.  sym     HTML symbol                       name                     Aw  melt    boil    dens       ABUNDe       ABUNDs         Rea  Max inspired pp
    Gas(AN_H,  "H",    "H<SUB><SMALL>2</SMALL></SUB>",   "Hydrogen",         1.0079,  14.06,  20.40,  8.99e-05,  0.00125893,  27925.4,       1,        0.0),
    Gas(AN_HE, "He",   "He",                             "Helium",           4.0026,   3.46,   4.20,  0.0001787, 7.94328e-09, 2722.7,        0,        MAX_HE_IPP),
    Gas(AN_N,  "N",    "N<SUB><SMALL>2</SMALL></SUB>",   "Nitrogen",        14.0067,  63.34,  77.40,  0.0012506, 1.99526e-05, 3.13329,       0,        MAX_N2_IPP),
    Gas(AN_O,  "O",    "O<SUB><SMALL>2</SMALL></SUB>",   "Oxygen",          15.9994,  54.80,  90.20,  0.001429,  0.501187,    23.8232,       10,       MAX_O2_IPP),
    Gas(AN_NE, "Ne",   "Ne",                             "Neon",            20.1700,  24.53,  27.10,  0.0009,    5.01187e-09, 3.4435e-5,     0,        MAX_NE_IPP),
    Gas(AN_AR, "Ar",   "Ar",                             "Argon",           39.9480,  84.00,  87.30,  0.0017824, 3.16228e-06, 0.100925,      0,        MAX_AR_IPP),
    Gas(AN_KR, "Kr",   "Kr",                             "Krypton",         83.8000, 116.60, 119.70,  0.003708,  1e-10,       4.4978e-05,    0,        MAX_KR_IPP),
    Gas(AN_XE, "Xe",   "Xe",                             "Xenon",          131.3000, 161.30, 165.00,  0.00588,   3.16228e-11, 4.69894e-06,   0,        MAX_XE_IPP),
    #                                                                     from here down, these columns were originally:      0.001,         0
    Gas(AN_NH3, "NH3", "NH<SUB><SMALL>3</SMALL></SUB>", "Ammonia",          17.0000, 195.46, 239.66,  0.001,     0.002,       0.0001,        1,        MAX_NH3_IPP),
    Gas(AN_H2O, "H2O", "H<SUB><SMALL>2</SMALL></SUB>O", "Water",            18.0000, 273.16, 373.16,  1.000,     0.03,        0.001,         0,        0.0),
    Gas(AN_CO2, "CO2", "CO<SUB><SMALL>2</SMALL></SUB>", "Carbon Dioxide",   44.0000, 194.66, 194.66,  0.001,     0.01,        0.0005,        0,        MAX_CO2_IPP),
    Gas(AN_O3,  "O3",  "O<SUB><SMALL>3</SMALL></SUB>",  "Ozone",            48.0000,  80.16, 161.16,  0.001,     0.001,       0.000001,      2,        MAX_O3_IPP),
    Gas(AN_CH4, "CH4", "CH<SUB><SMALL>4</SMALL></SUB>", "Methane",          16.0000,  90.16, 109.16,  0.010,     0.005,       0.0001,        1,        MAX_CH4_IPP),
]

''' OTHER IMPORTANT GASES WE DON'T CURRENTLY HANDLE THIS WAY or with randomly different values.
  Gas(AN_NH3, "NH3", "NH<SUB><SMALL>3</SMALL></SUB>", "Ammonia",       17.0000, 195.46, 239.66,  0.001,     0.002,       0.001,         0.001,    MAX_NH3_IPP),
  Gas(AN_H2O, "H2O", "H<SUB><SMALL>2</SMALL></SUB>O", "Water",         18.0000, 273.16, 373.16,  1.000,     0.03,        0.001,         0,        (9.9999E37)),
  Gas(AN_CO2, "CO2", "CO<SUB><SMALL>2</SMALL></SUB>", "Carbon Dioxide",44.0000, 194.66, 194.66,  0.001,     0.01,        0.001,         0,        MAX_CO2_IPP),
  Gas(AN_O3,   "O3", "O<SUB><SMALL>3</SMALL></SUB>",  "Ozone",         48.0000,  80.16, 161.16,  0.001,     0.001,       0.001,         0.001,    MAX_O3_IPP),
  Gas(AN_CH4, "CH4", "CH<SUB><SMALL>4</SMALL></SUB>", "Methane",       16.0000,  90.16, 109.16,  0.010,     0.005,       0.001,         0,        MAX_CH4_IPP),

  Gas(AN_F,  "F",  "F",                              "Fluorine",        18.9984,  53.58,  85.10,  0.001696,  0.000630957, 0.000843335,   50,    MAX_F_IPP),
  Gas(AN_CL, "Cl", "Cl",                             "Chlorine",        35.4530, 172.22, 239.20,  0.003214,  0.000125893, 0.005236,      40,    MAX_CL_IPP),

  Gas( 910, "H2", "H2",  2, 14.06, 20.40, 8.99e-05,  0.00125893, 27925.4  ),
  Gas( 911, "N2", "N2", 28, 63.34, 77.40, 0.0012506, 1.99526e-05,3.13329  ),
  Gas( 912, "O2", "O2", 32, 54.80, 90.20, 0.001429,  0.501187, 23.8232, 10),
  Gas(AN_CH3CH2OH, "CH3CH2OH", "Ethanol",  46.0000, 159.06, 351.66,  0.895,     0.001,       0.001,         0),
'''
