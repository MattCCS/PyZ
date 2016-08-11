"""
...

Author: Matthew Cotton
"""

# standard
from collections import OrderedDict

# custom
from pyz import colors
from pyz.curses_prep import curses, CODE

####################################

def say(s, r=400):
    import subprocess
    subprocess.check_output(['say', s, '-r', str(r)])

DEFAULT_COLOR = "white"
DEFAULT_MODE = curses.A_NORMAL

####################################

def get(name):
    return LayerManager.get(name)

def delete(name):
    LayerManager.delete(name)

####################################

class LayerManager(object):

    registry = {}

    def __init__(self, name, dims, wrap=False, restrict=False, sublayers=None):
        self.w, self.h = dims
        try:
            get(name)
            raise RuntimeError("Layer name {} already exists!".format(repr(name)))
        except KeyError:
            self.name = name

        if sublayers is None:
            sublayers = []

        self.restrict = restrict
        self.wrap = wrap
        self.points = {}
        self.layers = OrderedDict()     # string -> (x, y, layer) (ORDER MATTERS!)

        LayerManager.registry[name] = self

        for (x, y, each) in sublayers:
            self.add_layer(x, y, each)

    @staticmethod
    def get(name):
        return LayerManager.registry[name]

    @staticmethod
    def delete(name):
        try:
            del LayerManager.registry[name]
        except KeyError:
            pass

    ####################################
    # utilities
    def size(self):
        return (self.w, self.h)

    def convert_to_1d(self, x, y):
        return self.w * y + x

    def convert_to_2d(self, i):
        (y,x) = divmod(i, self.w)
        return (x,y)

    def out_of_bounds(self, x, y):
        return not (0 <= x < self.w) or not (0 <= y < self.h)

    def layer_out_of_bounds(self, x, y, layer):
        (w, h) = layer.size()
        return any([
            self.out_of_bounds(x,     y),
            self.out_of_bounds(x+w-1, y),
            self.out_of_bounds(x,     y+h-1),
            self.out_of_bounds(x+w-1, y+h-1),
            ])

    def reset(self):
        self.points = {}

    def reset_recursive(self):
        self.reset()
        for (_, _, layer) in list(self.layers.values()):
            layer.reset_recursive()

    ####################################
    # resizing
    def resize_diff(self, dw=0, dh=0):
        (w,h) = self.size()
        w += dw
        h += dh
        self.resize(w, h)

    def resize(self, w=0, h=0):
        (ow, oh) = self.size()

        self.w = w if w > 0 else ow
        self.h = h if h > 0 else oh

        self.on_resize()

    def on_resize(self):
        """
        Called on resize event

        Use for things like drawing borders
        """
        pass

    ####################################
    # setting points
    def set(self, x, y, char, color=None, mode=1):
        if type(char) is not int:
            assert len(char) == 1
        self.points[(x,y)] = (
            char,
            color if color is not None else DEFAULT_COLOR,
            mode if mode is not None else DEFAULT_MODE,
            )

    def unset(self, x, y):
        try:
            del self.points[(x,y)]
        except KeyError:
            pass

    ####################################
    # setting ranges
    def setlines(self, x, y, lines, color=None, mode=1):
        """
        For convenience, to allow blocks of text to be pre-written and split.
        """
        for (i,line) in enumerate(lines):
            self.setrange(x, y+i, line, color=color, mode=mode)

    def setrange(self, x, y, it, color=None, mode=1):
        for (i, c) in enumerate(it, x):
            # if not allow_beyond:
            #     if self.out_of_bounds(i, y):
            #         break
            self.set(i, y, c, color=color, mode=mode)

    ####################################
    # pre-paired ranges
    def setrange_paired(self, x, y, it):
        for (i, (c, color, mode)) in enumerate(it, x):
            # if not allow_beyond:
            #     if self.out_of_bounds(i, y):
            #         break
            self.set(i, y, c, color=color, mode=mode)

    ####################################
    # iterating over lines
    def yield_rows_with_none(self):
        for y in range(self.h):
            yield (self.points.get((x,y), None) for x in range(self.w))

    def items(self):

        # if wrap:
        #     for ((x,y),p) in self.points.iteritems():
        #         (x,y) = self.convert_to_2d(self.convert_to_1d(x,y))
        #         if self.out_of_bounds(x,y):
        #             continue # because iteritems has no order, we can't break :/
        #         yield (x, y, p)
        # else:
        for ((x,y),p) in self.points.items():
            yield (x, y, p)

    ####################################
    # manager operations
    def get_layer(self, name):
        return self.layers[name]

    def add_layer(self, x, y, layer):
        self.layers[layer.name] = (x,y,layer)

    def delete_layer(self, name):
        del self.layers[name]

    def move_layer(self, x, y, name):
        (_, _, layer) = self.get_layer(name)
        if self.restrict:
            if self.layer_out_of_bounds(x, y, layer):
                return False
        self.delete_layer(name)
        self.add_layer(x, y, layer)
        return True

    def move_layer_inc(self, x, y, name):
        (sx, sy, layer) = self.get_layer(name)
        x = sx + x
        y = sy + y
        return self.move_layer(x, y, name)

    ####################################
    # rendering
    def self_items(self):
        for ((x,y),p) in self.points.items():
            yield (x, y, p)

    def render_dict(self):
        points = {}

        # render sub-layers, in order
        for (ox, oy, layer) in list(self.layers.values()):
            for (x, y, point) in layer.render_to(ox, oy):
                if self.out_of_bounds(x,y):
                    continue
                points[(x,y)] = point

        # render self on top
        for (x, y, point) in self.self_items():
            if self.wrap:
                (x,y) = self.convert_to_2d(self.convert_to_1d(x,y))
            if self.out_of_bounds(x, y):
                continue
            points[(x,y)] = point

        return points

    def items(self, wrap=None):
        for ((x,y),p) in self.render_dict().items():
            yield (x, y, p)

    def render_to(self, ox, oy, wrap=None):
        for (x, y, point) in self.items(wrap=wrap):
            yield (x+ox, y+oy, point)

    ####################################
    # debug functions
    def debug_layers(self):
        for (name, (x,y,layer)) in list(self.layers.items()):
            print(("{}: pos={}/{} dims={}".format(name, x,y, layer.size())))

    def yield_rows_with_none(self):
        points = self.render_dict()
        for y in range(self.h):
            yield (points.get((x,y), None) for x in range(self.w))

    def debugrender(self, space=True):
        return '\n'.join((' ' if space else '').join((p[0] if p is not None else ' ') for p in row) for row in self.yield_rows_with_none())

####################################

# there will be, after initscr

CHARSETS = {
    "curses" : [],
    "ascii"  : '++++-|-|',
}

def set_curses_border():
    CHARSETS['curses'] = [
        curses.ACS_ULCORNER,
        curses.ACS_URCORNER,
        curses.ACS_LLCORNER,
        curses.ACS_LRCORNER,
        curses.ACS_HLINE,
        curses.ACS_VLINE,
        curses.ACS_HLINE,
        curses.ACS_VLINE,
    ]

def add_border(layer, charset='curses', chars=None, color=None):
    if chars:
        charset = chars
    else:
        charset = CHARSETS[charset]
    (x,y) = layer.size()
    tl, tr, bl, br, up, right, down, left = charset

    layer.setrange(0,   0, [tl]+[up]*(x-2)+[tr], color=color)
    layer.setrange(0, y-1, [bl]+[down]*(x-2)+[br], color=color)
    for oy in range(y-2):
        layer.set(  0, oy+1,  left, color=color)
        layer.set(x-1, oy+1, right, color=color)

####################################

import sys
PYTHON2 = sys.version_info[0] == 2

def set_bitmask(value):
    global FINAL_BITMASK
    FINAL_BITMASK = value

def set_dim(value):
    global DIM
    DIM = value

DIM = False
FINAL_BITMASK = 0

####################################

def render_to(main_layer, stdscr, offset_x=0, offset_y=0):
    global FINAL_BITMASK
    global DIM

    # stdscr.erase()

    for (x, y, (char_or_code, fg_bg, _)) in list(main_layer.items()):
        if DIM:
            fg_bg = colors.scale_fg_bg(fg_bg, 0.25)
        try:
            x = x + offset_x
            y = y + offset_y
            if type(char_or_code) is int:
                stdscr.addch(y, x, char_or_code, fg_bg | FINAL_BITMASK)
            else:
                stdscr.addstr(y, x, char_or_code if not PYTHON2 else char_or_code.encode(CODE), fg_bg | FINAL_BITMASK)
        except curses.error:
            break

    stdscr.refresh()
