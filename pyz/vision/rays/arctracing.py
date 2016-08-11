
import math

from pyz.vision import arc_tools
from pyz.vision import shell_tools
from pyz.vision import utils

####################################

def magnitude(coord):
    return math.hypot(*coord)

####################################

def perpendicular(coord):
    (x,y) = coord
    return (y,-x)

def normalize(coord, factor=1.0):
    """Not precise (floats, not Fractions)"""
    (x,y) = coord
    factor = math.hypot(x,y) / factor
    return (x/factor, y/factor)

def c_plusorminus_c(coord, coord_diff):
    """Returns low/high (or rather, first/second)"""
    (x,y) = coord
    (dx,dy) = coord_diff
    return (x+dx,y+dy), (x-dx,y-dy)

def edges_of_coord(coord, radius=0.5):
    try:
        perp = perpendicular(coord)
        perp = normalize(perp, radius) # +- 0.5 gives a range of 1
        (low, high) = c_plusorminus_c(coord, perp)
        high = int(round(arc_tools.convert_2D_coord_to_angle(high)))
        low  = int(round(arc_tools.convert_2D_coord_to_angle(low )))
    except ZeroDivisionError:
        (low, high) = (0, 360) # all points...?
        # TODO:  TEST THIS ^

    return (low, high)

####################################

def coords_behind_2D_perpwall(coord, angletable_2D=arc_tools.TABLE, shellcache=shell_tools.CACHE):

    # 'high' should be bigger -- if not, we have a wraparound scenario
    (low, high) = edges_of_coord(coord)
    # print low, high
    if low > high:
        # wraparound, correct terms
        (low, high) = (high, low)
        between = angletable_2D.between(0, low) | angletable_2D.between(high, 360) - set([coord])
    else:
        between = angletable_2D.between(low, high) - set([coord]) # <---<<< !!! THIS IS CRUCIAL!  Otherwise blocking propagates?

    mag = int(round(magnitude(coord)))

    return utils.fast_hemiarc(between, mag, shellcache)

def form_blocktable2D(angletable_2D=arc_tools.TABLE, shellcache=shell_tools.CACHE):
    coords = shellcache.coords()
    return {coord : coords_behind_2D_perpwall(coord, angletable_2D, shellcache) for coord in coords}

####################################
# SETUP

print("Forming BlockTable2D()...")
BLOCKTABLE = form_blocktable2D()

####################################

if __name__ == '__main__':

    # TODO:
    # RETHINK:  rather than recreate a small angle table,
    #           save the global angle table!

    coord = (7,3)
    print((BLOCKTABLE[coord]))
