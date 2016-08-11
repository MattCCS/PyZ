
import random

####################################

CLASSES = ["object", "item", "node"]

# meta
ATTRIBUTES  = {}
PARAMETERS  = {}

# sub-meta
MATERIALS   = {}

# concrete for the player
OBJECTS     = {}
ITEMS       = {}
NODES       = {}

# misc, maybe for testing
OTHER       = {}

####################################

def reset(obj, cat, name):
    """
    Set the default fields of the given object to those of the given name.

    ex:  set('grass', 'node', obj)
    ex:  set('grass', 'object', obj)
    """
    assert cat in CLASSES
    if cat == "node":
        NODES[name].set(obj)
    elif cat == "item":
        ITEMS[name].set(obj)
    elif cat == 'object':
        OBJECTS[name].set(obj)
    else:
        raise NotImplementedError()


class DataObject(object):
    """
    Represents the stored default data for an object or node.
    """

    def __init__(self, cat, name, data):
        assert cat in CLASSES
        self.name = name
        self.cat = cat
        self.__dict__.update(data)
        if cat == "node":
            NODES[self.name] = self
        elif cat == "object":
            OBJECTS[self.name] = self
        elif cat == "item":
            ITEMS[self.name] = self
        else:
            pass

    def set(self, obj):
        """
        Sets the default fields of this DataObject onto the given object.
        """

        for attr in list(ATTRIBUTES.keys()):
            setattr(obj, attr, False)
        for (key, val) in list(vars(self).items()):
            setattr(obj, key, val)
        if "colors" in vars(self):
            obj.color = random.choice(self.colors)
            obj.old_color = obj.color
        if "appearances" in vars(self):
            obj.appearance = random.choice(self.appearances)

    def __getattr__(self, key):
        """Sexy."""

        # DO error if asked for missing field:
        if not key in vars(self) and key in ATTRIBUTES:
            return False
        else:
            return vars(self)[key]

        # DO NOT error if asked for missing field:
        # if not key in self.__dict__:
        #     if key in ATTRIBUTES:
        #         return False
        #     else:
        #         raise AttributeError()
        # else:
        #     return self.__dict__[key]
