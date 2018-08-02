import inspect
import logging

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


