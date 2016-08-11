# encoding: utf-8

"""
"""

# custom
from pyz import node
from pyz import colors
from pyz import settings

####################################

BORDER_BLOCK = u'█'

####################################

def yield_coords(range_nums):
    if not range_nums:
        yield tuple()
        return

    # we want to iterate like Z/Y/X <--- better solution?
    first = range_nums[0]
    rest  = range_nums[1:]

    for n in range(first):
        for coord in yield_coords(rest):
            yield (n,) + coord

####################################

class Grid2D(object):

    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.nodes = {coord : node.Node2D(self, coord) for coord in yield_coords( (self.x, self.y) )}


def frame_coords_2d(width, height, ppos):
    """Yields relevant absolute coordinates to render"""
    (player_x, player_y) = ppos

    half_w = width//2
    half_h = height//2

    for abs_y in range(player_y-half_h, player_y+half_h):
        yield [(abs_x, abs_y) for abs_x in range(player_x-half_w, player_x+half_w+1)]


def xy_to_screen(coord, ppos, width, height, spacing=2):
    """Converts absolute coord to be relative to screen (with player at center)"""
    (abs_x, abs_y) = coord
    (player_x, player_y) = ppos

    rel_x = abs_x*spacing - player_x*spacing + width//2
    rel_y = height//2 - abs_y + player_y

    return (rel_x, rel_y)


def render_grid(visible, ppos, layer, nodes, spacing=2):

    (px,py) = ppos

    (w,h) = layer.size()

    for row in frame_coords_2d(w, h, ppos):

        for (x,y) in row:

            (abs_x, abs_y) = xy_to_screen( (x,y), (px,py), w, h, spacing=spacing )

            if not (x, y) in nodes:
                layer.set(abs_x, abs_y, BORDER_BLOCK, color=colors.get("white"))
                # pass
            elif not (x-px, y-py) in visible:
                # TODO: what does this do?
                # X/Y are REAL coords (non-relative)
                # so to check for visibility, we have to relativize them
                pass
            else:
                try:
                    nodes[(x,y)].render(layer, abs_x, abs_y)
                except KeyError:
                    pass # node out of bounds

def lookup(coord):
    return GRID.nodes[coord]

GRID = Grid2D(settings.WIDTH, settings.HEIGHT)

