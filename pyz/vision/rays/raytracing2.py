#!/usr/bin/env python

import math

from fractions import Fraction

def case(n):
    return 1 if n >= 0 else -1

def gen_origin(n):
    return [Fraction(0.5)] * n

def fractify(tup):
    return tuple(map(Fraction, tup))

# @profile
def normalize(vector_fractions):
    """
    
    """

    max_fract = max(vector_fractions, key=lambda n: abs(float(n)))

    if float(max_fract) == 0:
        raise ZeroDivisionError()

    factor = abs(1 / max_fract) # fraction

    normalized_to_1 = [factor * n for n in vector_fractions]

    return [n / 2 for n in normalized_to_1]  # normalized to 0.5
    # return normalized_to_1

# @profile
def trim_and_record(values, delta, cutoff=Fraction(0.5)):
    """
    Mutates the list!

    Does NOT do modular arithmetic!  Values should be NORMALIZED.
    """

    pairs = enumerate(values)
    pairs = sorted(pairs, key=lambda p: abs(p[1]), reverse=True)  # sort by largest diff

    cond = lambda n: abs(cutoff - n) >= cutoff

    double_cutoff = cutoff * 2

    for (i,v) in pairs:
        if not cond(v):
            continue

        values[i] -= case(delta[i]) * double_cutoff  # delta[i] IMPORTANT!!!
        yield i

# @profile
def gen_collision_path(slope_vector_fractions):
    """
    Uses (0.5, 0.5) as the center -- this way, there are 4(9) adjacent "vision" blocks,
    since we are making games with a text-centric concept of vision origin.  (0,0) makes no sense here.

    The problem with starting at (.5, .5) and adding to (1.5, whatever) is that
    the Y VALUE CAN CROSS THE THRESHOLD BEFORE THE X VALUE DOES, BUT WILL ALWAYS
    BR SURPASSED IF THE SLOPE IS (1, 0.6) BECAUSE (0.5, 0.9) + m = (1.5, 1.5)

    If we add half the slope instead, we get (1.0, 1.2) and we see that Y has beaten X.
    """

    slope_vector_fractions = fractify(slope_vector_fractions)

    if not any(slope_vector_fractions):
        yield slope_vector_fractions
        return

    delta = normalize(slope_vector_fractions)
    if max(list(map(abs, delta))) != 0.5:
        print(slope_vector_fractions, delta)
        raise RuntimeError("PROBLEM!  Probably supplied non-fractions.")

    cases = list(map(case, delta))    # ALWAYS INTEGERS

    mag = len(delta)
    new_coord = [0] * mag     # ALWAYS INTEGERS
    values = gen_origin(mag)  # "center" = (0.5, 0.5, 0.5)

    yield tuple(new_coord)

    while True:
        values = vector_sum(values, delta)

        for i in trim_and_record(values, delta, cutoff=Fraction(0.5)):
            new_coord[i] += cases[i]
            yield tuple(new_coord)


def string_to_vector(string):
    return list(map(Fraction, string.split(',')))


def find_slope(origin, destination):
    delta = vector_diff(origin, destination)

    return list(map(Fraction, delta))


def vector_sum(v1, v2):
    return list(map(lambda a,b: a+b, v1, v2))


def vector_diff(v1, v2):
    return list(map(lambda a,b: b-a, v1, v2))


def vector_magnitude(vector):
    return math.sqrt(sum([n**2 for n in vector]))


def vector_distance(v1, v2):
    return vector_magnitude(vector_diff(v1, v2))

# @profile
def gen_path_bounded_relative(slope_vector_fractions, bound_limit):
    slope_vector_fractions = fractify(slope_vector_fractions)

    path_gen = gen_collision_path(slope_vector_fractions)

    while True:
        coord = next(path_gen)  # always integer coords

        dist = vector_magnitude(coord)
        if dist > bound_limit:
            return

        yield coord  # allow equals

# @profile
def gen_path_bounded_absolute(origin, destination):
    origin      = fractify(origin)
    destination = fractify(destination)

    slope_vector_fractions = vector_diff(origin, destination)
    # print slope_vector_fractions

    bound_limit = vector_distance(origin, destination)
    # print bound_limit

    for coord in gen_path_bounded_relative(slope_vector_fractions, bound_limit):

        adjusted_coord = vector_sum(origin, coord)

        yield tuple(map(int, adjusted_coord))
