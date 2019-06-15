import ast
import astunparse
from IPython import get_ipython
from .logging import logger


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
