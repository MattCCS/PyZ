
# standard
import time

# custom
from pyz import colors
from pyz import objects
from pyz.curses_prep import curses
from pyz.curses_prep import CODE

####################################

class Node2D(objects.Parentable):

    ERROR  = '!'

    def __init__(self, parentgrid, coord):
        objects.Parentable.__init__(self, parent=None)

        self.parentgrid = parentgrid
        self.coord = coord

        self.reverse_video = False

        self.name = '---'
        self.appearance = None
        self.color = 0
        self.old_color = 0
        self.health = 0
        self._object_render_last_tick = 0
        self._object_render_threshold = 0.8
        self._object_render_index = 0 # always mod, in case this number has changed

    def position(self):
        return self.coord

    def superparent(self):
        return self

    def is_passable(self):
        return not any(obj.impassible for obj in self.objects)

    ####################################
    # attribute assignment

    def set(self, name):
        objects.reset(self, 'node', name)

    def add(self, name):
        objects.make(name, self)

    ####################################

    def render(self, layer, x, y):

        # base stuff
        char = self.appearance if self.appearance else Node2D.ERROR
        color = self.color

        # object stuff
        # TODO: NOTE: this forces objects to have an appearance!
        if self.objects:
            t = time.time() # TODO:  just save one value to the class.

            if abs(t - self._object_render_last_tick) > self._object_render_threshold:
                self._object_render_last_tick = t
                self._object_render_index += 1

            self._object_render_index %= len(self.objects)

            obj = self.objects[self._object_render_index]
            char = obj.appearance
            color = obj.color

        # gas/smoke stuff
        # ...

        color = colors.get(color)
        if self.reverse_video:
            color = color | curses.A_REVERSE # BITMASK!!!

        # actual settings
        layer.set(x, y, char.encode(CODE), color=color)
