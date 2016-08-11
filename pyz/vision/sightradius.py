
from pyz.vision.trees import fasttree
from pyz.vision.rays import arctracing
from pyz.vision import arc_tools
from pyz.vision import shell_tools
from pyz.vision import utils
from pyz import log
# from pyz import settings

####################################

class SightRadius2D(object):

    def __init__(self, radius, shellcache=shell_tools.CACHE, blocktable=arctracing.BLOCKTABLE):
        self.radius = radius
        self.shellcache = shellcache
        self.blocktable = blocktable

    def potentially_illuminated(self):
        # TODO:
        # this recalculates every tick
        return self.shellcache.coords_before(self.radius)

    def visible_coords(self, blocked_relative):
        return utils.remaining(self.potentially_illuminated(), blocked_relative, self.blocktable)


class ArcLight2D(SightRadius2D):

    def __init__(self, radius, angle, arc_length, shellcache=shell_tools.CACHE, blocktable=arctracing.BLOCKTABLE, angletable2D=arc_tools.TABLE):
        # super(ArcLight2D, self).__init__(radius, shellcache=shellcache, blocktable=blocktable)
        SightRadius2D.__init__(self, radius, shellcache=shellcache, blocktable=blocktable)
        self.angle = angle
        self.arc_length = arc_length
        self.angletable2D = angletable2D

    @log.logwrap
    def potentially_illuminated(self):
        potential = self.angletable2D.around(self.angle, self.arc_length) | set([(0,0)])
        return potential - utils.fast_hemiarc(potential, self.radius, self.shellcache)

    @log.logwrap
    def visible_coords(self, blocked_relative):
        # return utils.remaining(self.potentially_illuminated(), blocked_relative, self.blocktable)
        return self.potentially_illuminated()

    def set_angle(self, angle):
        self.angle = angle

    def set_arc(self, arc):
        self.arc_length = arc

