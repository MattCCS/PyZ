

class Event(object):
    """
    A class representing an abstract event
    to be resolved one step at a time.

    Does nothing when dead, but should be removed.
    """

    def __init__(self, manager, grid, layer, coord):
        self.manager = manager
        self.grid = grid
        self.layer = layer
        self.coord = coord

        self.dead = False

    def step(self):
        if self.dead:
            return


class GenericInteractVisualEvent(Event):

    def __init__(self, manager, grid, layer, coord):
        Event.__init__(self, manager, grid, layer, coord)
        self.manager.requested_waits.append(0.1)

        self.ticks = 2

        self.step() # initialize visual effect so it takes effect THIS turn

    def step(self):
        if self.dead:
            return

        node = self.grid.nodes[self.coord]
        if self.ticks == 2:
            node.reverse_video = True
        elif self.ticks == 1:
            node.reverse_video = False
        else:
            self.dead = True

        self.ticks -= 1


class GenericFocusEvent(Event):

    def __init__(self, manager, grid, layer, coord):
        Event.__init__(self, manager, grid, layer, coord)

        self.step()

    def step(self):
        if self.dead:
            return

        node = self.grid.nodes[self.coord]
        node.reverse_video = True
        self.dead = True


class FacingEvent(Event):

    def __init__(self, manager, grid, layer, coord, arc, start, target, speed):
        Event.__init__(self, manager, grid, layer, coord)

        assert 0 <= (start + target) <= 720
        assert speed > 0

        if start - target < -180:
            start += 360
        elif start - target > 180:
            target += 360

        # say("start is {}".format(start))
        # say("target is {}".format(target))

        self.angle = start
        self.target = target
        self.speed = speed

        self.arc = arc

        self.deathcounter = 1

        self.step()

    def step(self):

        if self.dead:
            return

        if self.angle > self.target:
            self.angle = max(self.target, self.angle - self.speed)
        elif self.angle < self.target:
            self.angle = min(self.target, self.angle + self.speed)

        self.arc.set_angle(self.angle % 360)
        # say("angle is now {}".format(self.arc.angle))
        
        if self.angle == self.target:
            self.deathcounter -= 1

        if self.deathcounter == 0:
            self.dead = True
