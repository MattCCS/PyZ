
import random

from pyz import audio
from pyz import events
from pyz import log
from pyz import data

from collections import OrderedDict

from pyz.vision import sightradius
from pyz.vision import arc_tools

####################################

def say(s, r=400):
    import subprocess
    subprocess.check_output(['say', s, '-r', str(r)])

CENTER = (0,0)

####################################

DAMAGE_DESCRIPTORS = [
    (0.1, "practically broken"),
    (0.2, "extremely damaged"),
    (0.3, "heavily damaged"),
    (0.4, "damaged"), # battered?
    (0.5, "cracked"),
    (0.6, "scraped"),
    (0.7, "dented"),
    (0.8, "scratched"),
    (0.9, "worn"),
    (1.0, ""),
]

def damage_descriptor(p):
    assert 0 <= p <= 1.0

    for (c, d) in DAMAGE_DESCRIPTORS:
        if p < c:
            val = d
            break
    else:
        val = ""

    return " " + val

####################################

def make(name, parent=None):
    """For objects and items"""

    if name in data.ITEMS:
        gob = Item(parent=parent)
        data.reset(gob, "item", name)
    else:
        gob = GameObject(parent=parent)
        data.reset(gob, "object", name)

    if parent is not None:
        parent.objects.add(gob)

    return gob

def spawn(owner, rate):
    # TODO: this seems slow, but it makes sense.

    for (obj_name, odds) in rate['any'].items():
        r = random.randint(1, sum(odds))
        for (idx, odd) in enumerate(odds):
            r -= odd
            if r <= 0:
                break

        for _ in range(idx): # python 2/3
            obj = make(obj_name, owner)

def reset(owner, cat, name):
    """For nodes?"""
    data.reset(owner, cat, name)
    if hasattr(owner, 'spawn_birth'):
        spawn(owner, owner.spawn_birth)

def occluders():
    return GameObject.occluders()

####################################

class ObjectSet(object):

    def __init__(self):
        self.objects = OrderedDict()

    def add(self, *objects):
        for obj in objects:
            self.objects[obj] = None

    def drop(self, *objects):
        for obj in objects:
            self.objects.pop(obj)

    def __iter__(self):
        return iter(self.objects.keys())

    def __contains__(self, obj):
        return obj in self.objects

    def __len__(self):
        return len(self.objects)

    def __getitem__(self, index):
        return list(self.objects.keys())[index] # python 2/3

####################################

class Parentable(object):
    
    def __init__(self, parent=None):
        self.objects = ObjectSet()
        self.parent = None
        self.set_parent(parent)

    def superparent(self):
        if self.parent:
            return self.parent.superparent()
        else:
            return self

    def position(self):
        if self.parent is None:
            raise RuntimeError("No parent, so no position! {} {}".format(self, vars(self)))
        else:
            return self.parent.position()

    def set_parent(self, new_parent):
        # TODO: consider making __.objects a set.
        self.remove_parent()
        self.parent = new_parent
        if self.parent:
            if not self in self.parent.objects:
                self.parent.objects.add(self)

    def remove_parent(self):
        if self.parent:
            if self in self.parent.objects:
                self.parent.objects.drop(self)
            self.parent = None


####################################

class GameObject(Parentable):
    """
    A GameObject is any physically-interactive
    *thing* in the game world (that takes up one space).
    """

    record = []

    @staticmethod
    def age_all(manager, grid, layer):
        for obj in GameObject.record:
            obj.age(manager, grid, layer)

    @staticmethod
    def kill_dead():
        dead = [obj for obj in GameObject.record if obj.dead]
        for obj in dead:
            GameObject.record.remove(obj)  # remove from record
            # obj.parent.objects.remove(obj) # remove from parent
            # del obj

    @staticmethod
    def occluders():
        """Dynamic!"""
        return (obj for obj in GameObject.record if obj.occluder)
    
    ####################################

    def __init__(self, parent):
        Parentable.__init__(self, parent=parent)
        self.dead = False
        GameObject.record.append(self)

    def age(self, manager, grid, layer):
        pass

    def damage(self, n):
        if not hasattr(self, 'health'):
            return

        if self.damageable:
            self.health -= n
            if self.health <= 0:
                self.die()

    def die(self):
        # self.parentgrid.news.add("The {} dies.".format(self.name))
        self.dead = True
        if hasattr(self, "s_death"):
            (sound, volume) = self.s_death['sound'], self.s_death['volume']
            audio.play_random(sound, volume)
        if hasattr(self, 'spawn_death'):
            spawn(self.superparent(), self.spawn_death)
            pass
        self.remove_parent()

    ####################################

    def __getattr__(self, key):
        """Sexy."""

        # DO error if asked for missing field:
        if not key in vars(self) and key in data.ATTRIBUTES:
            return False
        else:
            return vars(self)[key]


class Item(GameObject):
    """
    An Item is a subset of GameObject -- it is a
    physically-interactive *thing* because we can
    place it/throw it/inspect it/etc., but it is
    also something that can be held/used/put in inventory.
    """

    record = []
    
    def __init__(self, parent):
        GameObject.__init__(self, parent=parent)
        Item.record.append(self)

# TODO
# NOTE: don't call super if you care what is called/when/with what; call __init__ instead

class Lantern(Item, sightradius.SightRadius2D):
    """
    Represets a radial light source.
    """

    def __init__(self, radius, parent, lifetick=20):
        Item.__init__(self, parent=parent)
        sightradius.SightRadius2D.__init__(self, radius) # default shellcache/blocktable

        self.can_age = False
        self.lifetick = lifetick
        self.ticks = self.lifetick

    def age(self, manager, grid, layer):
        if not self.can_age:
            return

        if not self.ticks:
            self.ticks = self.lifetick
            self.radius = max(0, self.radius - 1)
        else:
            self.ticks -= 1


class Flashlight(Item, sightradius.ArcLight2D):
    """
    Represets a directed radial light source.
    """

    def __init__(self, radius, arc_length, parent, angle=0):
        Item.__init__(self, parent=parent)
        sightradius.ArcLight2D.__init__(self, radius, angle, arc_length) # default shellcache/blocktable/angletable

        self.on = False
        self.focus = (20, 30)
        self.modes = ['static', 'facing', 'focus']
        self.mode = 1
        self.focus_threshold = self.arc_length / 2
        self.focus_speed = 12

    def visible_coords(self, blocked_relative):
        if not self.on:
            return set()
        else:
            return sightradius.ArcLight2D.visible_coords(self, blocked_relative)

    def toggle(self):
        audio.play("items/flashlight_toggle.m4a", volume=3.0)
        self.on = not self.on
        return self.on

    def swivel(self, diff, manager, grid, layer):
        self.mode = 0 # OVERRIDE
        target = (self.angle + diff) % 360
        manager.visual_events_bottom.append(events.FacingEvent(manager, grid, layer, None, self, self.angle, target, self.focus_speed))

    def toggle_mode(self):
        audio.play("weapons/trigger.aif", volume=0.2)
        self.mode = (self.mode + 1) % len(self.modes)
        return self.modes[self.mode]

    def is_focusing(self):
        return self.modes[self.mode] == 'focus'

    def target_angle_diff(self):
        return int(round(arc_tools.relative_angle(self.position(), self.focus)))

    def facing_away(self):
        return abs(self.target_angle_diff() - self.angle) > self.focus_threshold

    def update(self, manager, grid, layer):
        target = self.target_angle_diff()
        manager.visual_events_bottom.append(events.FacingEvent(manager, grid, layer, None, self, self.angle, target, self.focus_speed))
        manager.visual_events_top.append(events.GenericFocusEvent(manager, grid, layer, self.focus))

    def update_direction(self, direction):
        if self.modes[self.mode] != 'facing':
            return

        if direction == (1,0):
            self.angle = 0
        elif direction == (0,1):
            self.angle = 90
        elif direction == (-1,0):
            self.angle = 180
        elif direction == (0,-1):
            self.angle = 270

    def age(self, manager, grid, layer):
        if self.on and self.is_focusing() and self.facing_away():
            self.update(manager, grid, layer)


class Weapon(Item):

    def __init__(self, parent, typ, beats, damage, damagetype):
        Item.__init__(self, parent=parent)
        self.typ = typ

        self.beats = beats

        self.damage = damage
        self.damagetype = damagetype # damagetype vs beats??

    @log.logwrap
    def attack(self, obj, manager, grid, layer):
        # damage conditional on material?
        audio.play_attack(self.typ, obj.material)
        manager.visual_events_top.append(events.GenericInteractVisualEvent(manager, grid, layer, obj.position()))
        if obj.material in self.beats:
            obj.damage(self.damage)

WEAPONS = {}
WEAPONS['axe1'] = Weapon(None, 'axe', ['cloth', 'wood'], 1, 'slicing')
# piercing/blunt/slicing/crushing?

