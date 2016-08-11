
from pyz.vision.rays import raytracing2
from pyz.vision import shell_tools

####################################

def origin(dimensions):
    return (0,) * dimensions

####################################

def all_paths_to_points(points, listify=False):

    if not points:
        raise StopIteration

    # could be list or set we're given
    try:
        l = len(points[0])
    except TypeError:
        e = points.pop()
        l = len(e)
        points.add(e)

    center = (0,) * l

    for coord in points:
        path = raytracing2.gen_path_bounded_absolute(center, coord)
        # path = raytracing2.get_path(center, coord)

        if listify:
            path = list(path) # defeats the purpose of an iterator!

        yield path

####################################

def generate_all_rays(shell, dimensions):
    return [list(raytracing2.gen_path_bounded_absolute( origin(dimensions), coord )) for coord in shell]

def form_ray_lookup_table(all_rays):
    return [(ray, {coord:i for (i,coord) in enumerate(ray)}) for ray in all_rays]

def all_hit_by(start, ray_lookup_table):
    """Returns every coord even REMOTELY GRAZED by the given start coord"""
    hit = set()

    # all rays should be:
    # (ray, rayset)
    # --> ray = [coords]
    # --> rayset = {coord : i}
    #     ---> i = coord's index in 'ray'

    for (ray, rayset) in ray_lookup_table:
        if start in rayset:
            hit.update(ray[rayset[start]:])

    if start in hit:
        hit.remove(start)
    else:
        print(("START NOT IN RAY...?", start))

    return hit

####################################

def save_rays(n, dims=2):
    import sys

    print("Generating shell...")
    S = shell_tools.shell_wrap(n, dimensions=dims)
    print("done.")

    print("Sorting endpoints...")
    S = sorted(list(S))
    print("done.")
    
    l = len(S)
    print(("Endpoints: {}".format(l)))

    print("Generating all paths to points...")
    g = all_paths_to_points(S, listify=True)
    print("done.")

    print("Saving...")
    with open("RAYS_{}D_{}.txt".format(dims, n), 'w') as f:
        for (i,ray) in enumerate(g, 1):
            f.write(str(ray) + '\n')
            if not i % 1000: # every 1000 entries
                f.flush()
            sys.stdout.write("\r--> {} / {}".format(i, l))
            sys.stdout.flush()
    sys.stdout.write('\n')
    print("done.")
