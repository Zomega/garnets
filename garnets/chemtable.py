from attr import attr
from attr import attrs
import os
import pandas as pd

# This module is used for figuring out atmospheric chemistry, but it leaves
# some things to be desired. In particular, as coded, it does not really
# consider thick / thin atmospheres very well and does not consider reactions,
# either amoung gases in an atmosphere, or with regards to fixing in the crust.


@attrs
class Gas():
    num: int = attr()
    symbol: str = attr()
    name: str = attr()
    weight = attr()  # long double -- in atomic units.

    # TODO(woursler): Should use a phase diagram
    # -- these melting and boiling points are really simplistic
    # given the range of pressures things happen at.
    melt = attr()  # long double
    boil = attr()  # long double
    density = attr()  # long double

    # These somehow measure relative abundance, but I can't work out the difference from context.
    abunde = attr()  # long double
    abunds = attr()  # long double

    reactivity = attr()  # long double
    min_ipp = attr()
    max_ipp = attr()  # long double


def load_gases():
    local_dir = os.path.dirname(__file__)
    gases_filename = os.path.join(local_dir, 'data/gases.csv')
    gases = pd.read_csv(gases_filename)
    # NOTE: IPPs given in millibars
    # TODO(woursler): units... gases['weight'] = gases['weight'] * kg / mol
    return [
        Gas(**gas_row)
        for _, gas_row in gases.iterrows()
    ]


gases = load_gases()


def lookup_gas(symbol):
    for gas in gases:
        if gas.symbol == symbol:
            return gas
    raise NotImplementedError("Unknown Gas: " + symbol)
