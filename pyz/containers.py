"""
"""

# custom
from pyz.objects import Item

####################################

class Container(Item):

    def __init__(self, capacity, parent):
        Item.__init__(self, parent=parent)
        self.items = set()
        self.capacity = capacity
        self.remaining = self.capacity

    def store(self, item):
        if self.remaining - item.size < 0:
            return False
        else:
            self.remaining -= item.size
            self.items.add(item)
            item.set_parent(self)
            return True

    def remove(self, item):
        self.items.remove(item)
        item.set_parent(None)
        self.remaining += item.size

    # def remove_random(self):
    #     pass
