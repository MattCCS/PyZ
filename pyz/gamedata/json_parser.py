
import json
import os

from pyz import settings
from pyz import data
from pyz.gamedata import validation

####################################

DEBUG = False

def printdebug(s):
    if DEBUG:
        print(s)

RESERVED = {"description", "<obj>", "attributes", "material"}

DEFAULT_INDICATOR = "*"
REQUIRED_INDICATOR = "!"
ATTRIBUTES_INDICATOR = "attributes"
MATERIAL_INDICATOR = "material"

PARAM_EXCEPTIONS = []   # <---<<< these are ignored -- equiv. to commenting the JSON

####################################

def load_dict(path):
    return json.loads(open(path).read())

def load_attributes():
    attributes = load_dict(settings.ATTRIBUTES_PATH)

    for (name, attr) in list(attributes.items()):
        assert name not in data.ATTRIBUTES
        assert name not in data.PARAMETERS
        validation.validate_attribute(attr) # <3

    data.ATTRIBUTES.update(attributes)

def load_parameters():
    parameters = load_dict(settings.PARAMETERS_PATH)

    for (name, param) in list(parameters.items()):
        assert name not in data.ATTRIBUTES
        assert name not in data.PARAMETERS
        validation.validate_parameter(param) # <3

    data.PARAMETERS.update(parameters)

def load_materials():
    materials = load_dict(settings.MATERIALS_PATH)
    validate_and_correct_materials(materials)
    data.MATERIALS.update(materials)

def confirm_parameter(data_, param=None, param_name=None):
    if param is None:
        param = data.PARAMETERS[param_name]

    # COPY
    # print
    # print 'data:', data_
    # print 'param:', param
    if type(data_) is dict:
        data_ = dict(data_)
        if 'description' in data_:
            assert type(data_['description']) is str
            del data_['description']
    elif type(data_) is list:
        data_ = data_[:]
    param = dict(param)

    if 'description' in param:
        del param['description']

    if 'type' in param:
        assert len(param) == 1
        validation.TYPES[param['type']](data_) == data_
    elif '<obj>' in param:
        assert len(param) == 1 # TODO: ?
        for (ok, ov) in data_.items():
            # print ok
            # print ov
            # assert ok in data.OBJECTS
            confirm_parameter(ov, param=param['<obj>'])
    else:
        for (pk, pv) in param.items():
            assert pk in data_
            confirm_parameter(data_[pk], param=pv)
                

def validate_and_correct_materials(materials):

    # TODO: DEFAULTS AREN'T VALIDATED!  (well, they are later.)

    defaults  = materials.pop(DEFAULT_INDICATOR, {})

    for (name, mat) in list(materials.items()):
        assert name not in data.MATERIALS

        # defaults
        for (key, val) in defaults.items():
            if key not in mat:
                mat[key] = val # this is validated later...

        # parameters
        for (key, val) in list(mat.items()):
            if key in PARAM_EXCEPTIONS:
                continue
            if key == ATTRIBUTES_INDICATOR:
                continue
            if key == MATERIAL_INDICATOR:
                raise RuntimeError("materials can't contain materials!")
            if key == 'description':
                continue # TODO:

            confirm_parameter(val, param_name=key)

        # attributes
        if ATTRIBUTES_INDICATOR in mat:
            for attr in mat[ATTRIBUTES_INDICATOR]:
                assert attr in data.ATTRIBUTES
                mat[attr] = True
            del mat[ATTRIBUTES_INDICATOR]



def load_order():
    return open(settings.LOAD_ORDER).read().strip().split('\n')

####################################

def validate_and_save_objects(cat, objects, save=True):

    assert cat in ('object', 'item')

    # TODO: DEFAULTS AREN'T VALIDATED!  (well, they are later.)

    defaults = objects.pop(DEFAULT_INDICATOR, {})

    for (name, obj) in list(objects.items()):
        assert name not in data.OBJECTS

        # defaults
        for (key, val) in defaults.items():
            if key not in obj:
                obj[key] = val

        # material defaults (to be overridden, so only if not present)
        if MATERIAL_INDICATOR in obj:
            mat = data.MATERIALS[obj[MATERIAL_INDICATOR]]
            for (key, val) in mat.items():
                if key not in obj:
                    obj[key] = val

        # parameters
        for (key, val) in list(obj.items()):
            if key in PARAM_EXCEPTIONS:
                continue
            if key == ATTRIBUTES_INDICATOR:
                continue
            if key in data.ATTRIBUTES:
                continue
            if key == MATERIAL_INDICATOR:
                continue
            if key == 'description':
                continue # TODO:

            confirm_parameter(val, param_name=key)

        # attributes
        if ATTRIBUTES_INDICATOR in obj:
            for attr in obj[ATTRIBUTES_INDICATOR]:
                assert attr in data.ATTRIBUTES
                obj[attr] = True
            del obj[ATTRIBUTES_INDICATOR]

        if save:
            data.DataObject(cat, name, obj)

def validate_and_save_nodes(nodes):
    defaults = nodes.get(DEFAULT_INDICATOR, {})
    nodes.pop(DEFAULT_INDICATOR, None)

    for (node_name, node) in list(nodes.items()):
        printdebug('-'*20)
        printdebug("NN/N: {}/{}".format(node_name, node))
        for (param, val) in list(node.items()):
            printdebug("PARAM/VAL: {}/{}".format(param, val))
            if param in PARAM_EXCEPTIONS:
                printdebug("*IGNORING*")
                continue

            if param == ATTRIBUTES_INDICATOR:
                continue

            confirm_parameter(val, param_name=param)

        if ATTRIBUTES_INDICATOR in node:
            for attr in node[ATTRIBUTES_INDICATOR]:
                assert attr in data.ATTRIBUTES
                node[attr] = True
            del node[ATTRIBUTES_INDICATOR]

        data.DataObject("node", node_name, node)

####################################

def load_path(path):
    files = [f for f in os.listdir(settings.absolutize_gamedata(path)) if not f.startswith('.')]
    return files

def load_file(path):
    path = settings.absolutize_gamedata(path)
    return json.loads(open(path).read())

def load(path):
    # TODO: this is crap

    key = path.rstrip(os.path.sep)

    if path.endswith(os.path.sep):
        path = path.rstrip(os.path.sep)
        if path == 'objects':
            cat = 'object'
        elif path == 'items':
            cat = 'item'
        else:
            raise NotImplementedError()

        files = load_path(key)

        for filename in files:
            print(("... Loading {}...".format(filename)))
            validate_and_save_objects(cat, load_file(os.path.join(path, filename)))

    elif path.endswith('nodes'):
        node_data = load_file(path + '.json')
        validate_and_save_nodes(node_data)
    else:
        data.OTHER[key].update(load_file(path + '.json'))

def load_all():
    print("Loading attributes...")
    load_attributes()

    print("Loading parameters...")
    load_parameters()

    print("Loading materials...")
    load_materials()

    print("Loading load order...")
    rest = load_order()
    for each in rest:
        print(("Loading {}...".format(each)))
        load(each)

if __name__ == '__main__':
    load_all()
