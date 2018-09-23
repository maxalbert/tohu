import logging
import re
from graphviz import Digraph
from IPython.display import SVG

__all__ = ['DependencyGraph']

logger = logging.getLogger('tohu')


class DependencyGraph:

    NODE_ATTR = dict(shape='box', style='filled', fillcolor='white')

    def __init__(self, *, scale=1.0, name=None, graph_attr=None):
        graph_attr = graph_attr or dict()
        graph_attr['splines'] = 'ortho'
        self.graph = Digraph(name=name, node_attr=self.NODE_ATTR, graph_attr=graph_attr)
        self.scale = scale

    def __repr__(self):
        return f'<DependencyGraph>'

    def _repr_svg_(self):
        return self.get_svg(scale=self.scale)

    def add_node(self, g):
        self.graph.node(g.tohu_id, label=f'{g:long}')

    def add_edge(self, g1, g2, *, color='/paired3/2', style='solid', constraint=None):
        self.graph.edge(g1.tohu_id, g2.tohu_id, color=color, style=style, constraint=constraint)

    def add_subgraph(self, sg):
        assert isinstance(sg, DependencyGraph)
        self.graph.subgraph(sg.graph)

    def get_svg(self, scale=1.0):
        """
        Return string with an SVG representation of the graph.
        """
        svg = self.graph._repr_svg_()
        width, height = re.search('svg width="(\d+)pt" height="(\d+)pt"', svg).groups()
        width_new = int(scale * int(width))
        height_new = int(scale * int(height))
        svg_scaled = re.sub('svg width="\d+pt" height="\d+pt"', f'svg width="{width_new}pt" height="{height_new}pt"', svg)
        return svg_scaled

    def draw(self, scale=1.0):
        """
        Convenience method to draw a - possibly scaled - version of the graph in Jupyter notebooks.
        Returns an SVG object which is rendered automatically by the notebook.
        """
        return SVG(self.get_svg(scale=scale))