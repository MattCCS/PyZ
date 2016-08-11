
import math

from pyz.vision import shell_tools
from pyz import settings
from pyz.vision import utils

####################################

def relative_angle(c1, c2):
    rel = utils.coord_diff(c2, c1)
    return convert_2D_coord_to_angle(rel)

def convert_2D_coord_to_angle_no_remap(coord):
    return math.degrees(math.atan2(*coord[::-1]))

def convert_2D_coord_to_angle(coord):
    return convert_2D_coord_to_angle_no_remap(coord) % 360

# def coords_between_angles_2D(angle_table_2D, low, high):
#     return set().union(*angle_table_2D[low:high+1])

def angles_around_angle_2D(angle, arc_width):
    return (angle - arc_width, angle + arc_width)

# def coords_around_2D(angle_table_2D, angle, arc_width):
#     return coords_between_angles_2D(angle_table_2D, *angles_around_angle_2D(angle, arc_width))

####################################

def union_all(sets):
    return set().union(*sets)

def form_angle_table_2D(coords, accuracy):
    # V1
    # slower, but guaranteed symmetrical
    # return [set(c for c in coords if ang <= convert_2D_coord_to_angle(c) <= ang+1) for ang in range(360)]

    # table = []
    # for ang in range(360):
    #     sub = set(c for c in coords if ang <= convert_2D_coord_to_angle(c) <= ang+1)
    #     table.append(sub)
    #     print ang, len(coords)
    # return table

    # V2
    # faster, but may be asymmetrical?  maybe not?  depends on process/bounds.  test it out.
    table = []
    for ang in range(360):
        sub = set(c for c in coords if ang <= convert_2D_coord_to_angle(c) <= ang+1)
        table.append(sub)
        coords.difference_update(sub)
        # print ang, len(coords)
    return table


class AngleTable2D(object):

    def __init__(self, coords, accuracy=settings.ARC_ACCURACY):
        self.accuracy = accuracy
        self._table = form_angle_table_2D(coords, accuracy)

    def between(self, low, high):
        if low > high:
            # wraparound, correct terms
            (low, high) = (high, low)
            return self.between(0, low) | self.between(high, 360)
        else:
            return union_all(self._table[low:high])

    def around(self, angle, rad):
        low  = angle - rad
        high = angle + rad
        low %= 360
        high %= 360
        return self.between(low, high)


####################################
# SETUP
print(("Forming AngleTable2D({})...".format(len(shell_tools.CACHE.coords()))))
TABLE = AngleTable2D(shell_tools.CACHE.coords())
