import ast
import astunparse
from .logging import logger


def has_placeholder_kwargs(node):
    assert isinstance(node, ast.Call)

    def is_placeholder_node(nnn):
        is_generic_placeholder = isinstance(nnn.value, ast.Name) and nnn.value.id == "placeholder"
        is_custom_placeholder = isinstance(nnn.value, ast.Call) and nnn.value.func.id == "Placeholder"
        return is_generic_placeholder or is_custom_placeholder

    return any([is_placeholder_node(n) for n in node.keywords])


def is_tohu_foreach_decorator_node(node):
    return isinstance(node, ast.Call) and node.func.id == "foreach" and has_placeholder_kwargs(node)


def get_ast_node_for_classes_defined_interactively_in_ipython(cls):
    # The tohu generator class is being defined interactively in IPython
    assert __tohu_ipython_source_code_storer__.is_executing_cell
    _, orig_cls_ast_node = __tohu_ipython_source_code_storer__.cur_class_def_info[cls.__name__]

    # FIXME: the following will remove *all* foreach decorators, but if we're wrapping the class
    # in multiple ones then we should only remove the single one that's currently being applied!
    filtered_decorator_list = [
        x for x in orig_cls_ast_node.decorator_list if not is_tohu_foreach_decorator_node(x)
    ]

    orig_cls_ast_node.decorator_list = filtered_decorator_list
    orig_cls_ast_node = ast.Module(
        body=[orig_cls_ast_node]
    )  # wrap ClassDef node in Module so that it can be compiled
    return orig_cls_ast_node


class TohuIPythonSourceCodeStorer:

    def __init__(self):
        self.is_executing_cell = False
        self.cur_cell_source = None
        self.cur_class_def_info = {}

    def pre_run_cell(self, info):
        self.is_executing_cell = True
        self.cur_cell_source = info.raw_cell
        self.cur_class_def_info = {}

    def post_run_cell(self, result):
        self.is_executing_cell = False
        self.cur_cell_source = None
        self.cur_class_def_info = {}


__tohu_ipython_source_code_storer__ = TohuIPythonSourceCodeStorer()


class StoresClassSourceCodeAndAST(ast.NodeTransformer):

    def visit_ClassDef(self, node):
        node_source = astunparse.unparse(node)
        __tohu_ipython_source_code_storer__.cur_class_def_info[node.name] = (node_source, node)
        return node


def load_tohu_ipython_extension_if_available():
    try:
        from IPython import get_ipython
    except ImportError:
        # IPython is not available; no need to worry about interactively defined generator classes
        return

    ip = get_ipython()
    if not ip:
        # Not running in IPython; no need to worry about interactively defined generator classes
        return

    logger.debug("Loading tohu IPython extension.")
    ip.events.register("pre_run_cell", __tohu_ipython_source_code_storer__.pre_run_cell)
    ip.events.register("post_run_cell", __tohu_ipython_source_code_storer__.post_run_cell)
    ip.ast_transformers.append(StoresClassSourceCodeAndAST())
