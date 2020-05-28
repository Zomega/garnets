"""Chemicals and their basic physical properties.

This module is used for figuring out atmospheric chemistry, but it leaves
some things to be desired. In particular, as coded, it does not really
consider thick / thin atmospheres very well and does not consider reactions,
either amoung gases in an atmosphere, or with regards to fixing in the crust.
"""

import os
import pandas as pd

from attr import attr
from attr import attrs
from xatu.core import quantity_formatter
from xatu.units import g
from xatu.units import kg
from xatu.units import millibar
from xatu.units import mol
from xatu.units import K

# pylint: disable=too-few-public-methods


@attrs
class Gas():
    """Represents a substance that commonly occurs as a gas atmosphere."""

    num: int = attr()
    symbol: str = attr()
    name: str = attr()
    weight = attr(repr=quantity_formatter(g/mol))

    # TODO(woursler): Should use a phase diagram
    # -- these melting and boiling points are really simplistic
    # given the range of pressures things happen at.
    melt = attr()  # long double
    boil = attr()  # long double
    density = attr()  # long double

    # These somehow measure relative abundance,
    # but I can't work out the difference from context.
    abunde = attr()  # long double
    abunds = attr()  # long double

    reactivity = attr()  # long double
    min_ipp = attr()
    max_ipp = attr()  # long double


def load_gases():
    """Load all the known gases from a file on disk."""
    local_dir = os.path.dirname(__file__)
    gases_filename = os.path.join(local_dir, 'data/gases.csv')
    gases = pd.read_csv(gases_filename)
    gases['melt'] = gases['melt'] * K
    gases['boil'] = gases['boil'] * K
    gases['weight'] = gases['weight'] * kg / mol
    gases['min_ipp'] = gases['min_ipp'] * millibar
    gases['max_ipp'] = gases['max_ipp'] * millibar
    return [
        Gas(**gas_row)
        for _, gas_row in gases.iterrows()
    ]


GASES = load_gases()


def lookup_gas(symbol):
    """Look up a gas based on it's symbol."""
    for gas in GASES:
        if gas.symbol == symbol:
            return gas
    raise NotImplementedError("Unknown Gas: " + symbol)
