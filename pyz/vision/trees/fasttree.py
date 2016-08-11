
from pyz.vision.rays import arctracing
from pyz import settings
from pyz.vision import utils

import ast

####################################

FILENAME_FORM = "RAYS_{dimensions}D_{radius}.txt"

def filename_format(radius, dimensions):
    return FILENAME_FORM.format(radius=radius, dimensions=dimensions)

####################################

class SimpleView(object):

    def __init__(self, table=arctracing.BLOCKTABLE, radius=settings.MAX_RADIUS, dimensions=settings.DIMENSIONS):
        self.radius = radius
        self.dimensions = dimensions
        self.table = table  # coord -> everything it blocks (even partially)
        self.all = set(table.keys())

    def visible_coords(self, blocked):
        return utils.remaining(self.all, blocked, self.table)

    def save(self):
        return str(self.table)

    def filename(self):
        return filename_format(self.radius, self.dimensions)

####################################

def save(view):
    with open(view.filename(), 'w') as f:
        f.write(view.save())

def load(radius, dimensions):
    with open(filename_format(radius, dimensions), 'r') as f:
        return SimpleView(ast.literal_eval(f.read()), radius, dimensions)

####################################

# def gen_new(radius, dimensions):

#     # TODO:
#     # DOES NOT INCLUDE (0,0) !!!
#     # is that ok?
#     print "Generating radius:{} dimensions:{}".format(radius, dimensions)

#     print "Generating all points..."
#     all_points = shell_tools.shell_coords(0, radius, dimensions)

#     print "Generating endpoints..."
#     endpoints = shell_tools.shell_wrap(radius, dimensions)
#     # print "endpoints:", endpoints

#     print "Calculating all rays..."
#     all_rays = ray_tools.generate_all_rays(endpoints, dimensions)
#     # print "all rays:", all_rays

#     print "Forming all_rays lookup table..."
#     ray_lookup_table = ray_tools.form_ray_lookup_table(all_rays)

#     print "Finding all hit by..."
#     table = {}
#     for coord in all_points:
#         all_hit = ray_tools.all_hit_by(coord, ray_lookup_table)
#         table[coord] = all_hit

#     print "[!] Forming angle table..."
#     # we include BOTH end angles!
#     angle_table_2D = arc_tools.angle_table(table.iterkeys())

#     print "done."
#     return SimpleView(table, radius, dimensions), angle_table_2D

####################################

# def gen_new_all(radii=[8,12,16,24,32], dimensions=[2]):
#     for dim in dimensions:
#         for rad in radii:
#             print "Generating/saving radius:{} dimensions:{}".format(rad, dim)
#             save(gen_new(rad, dim))

####################################
# SETUP

print("Creating SimpleView()...")
VIEW = SimpleView()

####################################

if __name__ == '__main__':
    pass
    # (sv, at) = gen_new(8,2)
    # print sv
    # print sv.save()
    # print at

    # same:
    # print arc_tools.coords_between_angles_2D(at, *arc_tools.angles_around_angle_2D(15, 5))
    # print arc_tools.coords_around_2D(at, 15, 5)

    # gen_new_all()
    # gen_new_all(radii=[8,12,16,24,32], dimensions=[3])

