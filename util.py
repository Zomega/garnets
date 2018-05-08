# These are a bunch of functions and macros from stargen that either are redundant with default python functionality, or are not included somehow.
# Pretty much all of these should be removed.


def pow1_4(x):
    return x ** (1. / 4.)


def pow2(x):
    return x ** 2


def pow3(x):
    return x ** 3


def about(x, dx):
    raise NotImplementedError("about not implemented.")


def random_number(a, b):
    raise NotImplementedError("random_number not implemented.")


def random_eccentricity(a, b):
    raise NotImplementedError("random_number not implemented.")
