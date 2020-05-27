# These are a bunch of functions and macros from stargen that either
# are redundant with default python functionality, or are not included
# somehow. Pretty much all of these should be removed.
import random


def about(x, dx):
    return random.uniform(x - dx, x + dx)


def random_number(a, b):
    return random.uniform(a, b)


def random_eccentricity():
    return 0  # TODO(woursler): Something less boring.
