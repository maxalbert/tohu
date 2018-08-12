import inspect
import logging
from .generators import BaseGenerator, IterateOver

logger = logging.getLogger('tohu')


def restore_globals(global_vars, names, clashes):

    for name in names:
        if name in clashes:
            # restore items that were previously defined
            global_vars[name] = clashes[name]
        else:
            # remove items which didn't exist before
            global_vars.pop(name)


def with_context(**var_defs):
    new_names = var_defs.keys()
    parent_frame = inspect.currentframe().f_back
    global_vars = parent_frame.f_globals

    clashes = {name: global_vars[name] for name in new_names if name in global_vars}
    global_vars.update(var_defs)

    def identity(x):
        restore_globals(global_vars, new_names, clashes)
        return x

    return identity


def foreach(**var_defs):
    new_names = var_defs.keys()
    parent_frame = inspect.currentframe().f_back
    global_vars = parent_frame.f_globals

    if len(var_defs) != 1:
        raise ValueError("Foreach does not support more than one input generator at the moment")
    input_name, input_value = list(var_defs.items())[0]
    if not isinstance(input_value, BaseGenerator):
        if not isinstance(input_value, (list, tuple)):
            raise TypeError("Input value to foreach must be a tohu generator, list or tuple")
        var_defs = {input_name: IterateOver(input_value)}

    clashes = {name: global_vars[name] for name in new_names if name in global_vars}
    global_vars.update(var_defs)

    def identity(x):
        restore_globals(global_vars, new_names, clashes)
        return x

    return identity
