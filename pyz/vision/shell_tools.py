
import itertools

from pyz import settings

####################################

def plusAndMinusPermutations(items):
    for p in itertools.permutations(items):
        for signs in itertools.product([-1,1], repeat=len(items)):
            yield tuple(a*sign for a,sign in zip(p,signs))

def shell_coords(min_dist, max_dist, dimensions=2):

    if min_dist <= max_dist <= 0:
        return set( [(0,) * dimensions] )

    assert type(min_dist) is int
    assert type(max_dist) is int
    assert min_dist >= 0
    assert max_dist > min_dist

    # the idea:
    #   min_dist < sqrt(a^2 + b^2) <= max_dist

    high_bound = max_dist ** 2
    low_bound  = min_dist ** 2

    possible_not_max = list(range(max_dist))  # UP TO (but not including) MAX_DIST

    pow_sum_op = lambda p: sum([n**2 for n in p])

    found = set()

    # for example, for 2...3, we're going to loop through 0,1,2 to go next to a 2.
    # anything next to a 3 has to be 0, so we'll ignore that last loop op.

    # UP TO (but not including) MAX_DIST
    # don't repeat things like (0,1) and (1,0), as we'll make these anyways when we permute

    for rest in itertools.combinations(possible_not_max, dimensions-1):
        
        # don't bother unless you hit the minimum
        # don't include the high bound
        for i in range(int(min_dist/1.5), max_dist):  # /sqrt(2), really.

            tup = rest + (i,)

            pow_sum = pow_sum_op(tup)

            if not low_bound < pow_sum <= high_bound:  # WE DONT INCLUDE LOW BOUND!
                continue

            every = list(itertools.permutations(tup))

            found.update(every)

    # manually add the max coord
    max_coord = (0,) * (dimensions-1) + (max_dist,)
    every = itertools.permutations(max_coord)
    found.update(every)

    newfound = set()

    # I hate this, but it works simply.
    for each in found:

        for new in plusAndMinusPermutations(each):

            newfound.add(new)

    if min_dist == 0:
        newfound.add( (0,) * dimensions )

    return newfound


def shell_wrap(n, dimensions=2):
    return shell_coords(n-1, n, dimensions=dimensions)

def rings_from(a, b, dimensions=2):
    return [shell_wrap(n, dimensions=dimensions) for n in range(a,b)]

####################################

class ShellCache(object):

    def __init__(self, radius, dimensions=2):
        self.radius = radius
        self._shells = rings_from(0, radius+1, dimensions=dimensions)


    def shells(self):
        return self._shells

    def shells_between(self, low, high):
        return self._shells[low:high]

    def shells_before(self, high):
        return self._shells[:high]

    def shells_after(self, low):
        return self._shells[low:]


    def union(self, shells):
        return set().union(*shells)


    def coords(self):
        return self.union(self.shells())

    def coords_between(self, low, high):
        return self.union(self.shells_between(low, high))

    def coords_before(self, high):
        return self.union(self.shells_before(high))

    def coords_after(self, low):
        return self.union(self.shells_after(low))


    def visible_coords(self):
        return self.coords()

####################################
# SETUP

print(("Forming ShellCache({})...".format(settings.MAX_RADIUS)))
CACHE = ShellCache(settings.MAX_RADIUS)
