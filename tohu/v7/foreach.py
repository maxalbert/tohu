import ast
import inspect
import textwrap
from .base import TohuBaseGenerator
from .ipython_support import get_ast_node_for_classes_defined_interactively_in_ipython

__all__ = ["Placeholder", "placeholder", "foreach"]


class Placeholder:
    def __init__(self, name):
        self.name = name


placeholder = Placeholder("<generic>")


def get_ast_node_for_classes_defined_in_source_files(cls):
    orig_cls_source = textwrap.dedent(inspect.getsource(cls))
    orig_cls_ast_node = ast.parse(orig_cls_source)
    return orig_cls_ast_node


def get_cls_compiled_ast_node(cls):
    try:
        orig_cls_ast_node = get_ast_node_for_classes_defined_in_source_files(cls)
    except TypeError as exc:
        if exc.args[0] == "<module '__main__'> is a built-in class":
            orig_cls_ast_node = get_ast_node_for_classes_defined_interactively_in_ipython(cls)
        else:
            # unexpected error; re-raise the exception
            raise

    orig_cls_compiled = compile(orig_cls_ast_node, "<string>", "exec")
    return orig_cls_compiled


def reevaluate_class_definition(
    orig_cls_compiled_ast_node, *, orig_cls_name, global_vars, local_vars, **custom_var_defs
):
    my_global_vars = global_vars.copy()
    my_global_vars.update(custom_var_defs)
    my_global_vars.update(local_vars)
    my_local_vars = {}

    exec(orig_cls_compiled_ast_node, my_global_vars, my_local_vars)

    # Sanity check to ensure the code only evaluated the expected class definition
    assert list(my_local_vars.keys()) == [orig_cls_name], "Unexpected object(s) found during code evaluation."

    reevaluated_cls = my_local_vars[orig_cls_name]
    return reevaluated_cls


def restore_globals(global_vars, names, clashes):

    for name in names:
        if name in clashes:
            # restore items that were previously defined
            global_vars[name] = clashes[name]
        else:
            # remove items which didn't exist before
            global_vars.pop(name)


def foreach(**var_defs):
    new_names = var_defs.keys()
    parent_frame = inspect.currentframe().f_back
    global_vars = parent_frame.f_globals
    local_vars = parent_frame.f_locals

    clashes = {name: global_vars[name] for name in new_names if name in global_vars}
    global_vars.update(var_defs)

    def make_foreach_closure(cls):

        if not inspect.isclass(cls):
            raise TypeError(
                f"Foreach decorator must be applied to a tohu generator class, not an object of type {type(cls)}."
            )

        if not issubclass(cls, TohuBaseGenerator):
            raise TypeError("Decorated class must be a subclass of TohuBaseGenerator.")

        orig_cls_compiled_ast_node = get_cls_compiled_ast_node(cls)
        orig_cls_name = cls.__name__

        class ForeachWrapper:
            def __init__(self, *args, **kwargs):
                self.init_args = args
                self.init_kwargs = kwargs

            def foreach(self, **custom_var_defs):
                custom_var_names = list(custom_var_defs.keys())

                missing_params = list(set(new_names).difference(custom_var_names))
                extra_params = list(set(custom_var_names).difference(new_names))
                if missing_params:
                    raise ValueError(f"Missing parameter(s): {', '.join(missing_params)!r}")
                if extra_params:
                    raise ValueError(f"Extra parameter(s) provided: {', '.join(extra_params)!r}")

                # Re-evaluate the class definition, including the previously missing
                # variable values to replace the placeholders.
                rewritten_cls = reevaluate_class_definition(
                    orig_cls_compiled_ast_node,
                    orig_cls_name=orig_cls_name,
                    global_vars=global_vars,
                    local_vars=local_vars,
                    **custom_var_defs,
                )
                return rewritten_cls(*self.init_args, **self.init_kwargs)

        restore_globals(global_vars, new_names, clashes)

        return ForeachWrapper

    return make_foreach_closure
