# These are a bunch of functions and macros from stargen that either
# are redundant with default python functionality, or are not included
# somehow. Pretty much all of these should be removed.
import random


def pow1_4(x):
    return x**(1. / 4.)


def pow2(x):
    return x**2


def pow3(x):
    return x**3


def about(x, dx):
    return random.uniform(x - dx, x + dx)


def random_number(a, b):
    return random.uniform(a, b)


def random_eccentricity():
    return 0  # TODO(woursler): Something less boring.
