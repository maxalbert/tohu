import textwrap
from mako.template import Template

__all__ = ['DependencyGraph']


class DependencyGraph:

    def __init__(self, generator=None):
        self.node_indices = {}
        self.cnt = 0

        if generator is not None:
            self.add_node(generator)

    def add_node(self, node):
        if node not in self.node_indices:
            print(f"Adding node {node}")
            self.cnt += 1
            self.node_indices[node] = str(self.cnt)
        for n in node.parent_chain:
            self.add_node(n)
        for n in node._constituents:
            self.add_node(n)

    def __repr__(self):
        parent_chains = [self.get_parent_chain(n) for n in self.leaf_nodes if n.parent is not None]
        constituents = {self.node_indices[n]: [self.node_indices[c] for c in n._constituents] for n in self.node_indices if
                        n._constituents != []}
        return Template(textwrap.dedent("""\
            <DepGraph:
               Nodes:
               % for node, i in nodes:
                 ${i}: ${node}
               % endfor
               Ancestry:
               % for chain in parent_chains:
                 ${' -> '.join(chain)}
               % endfor
               Constituents:
               % for n, c in constituents.items():
                 ${n}: ${', '.join(c)}
               % endfor
             >""")).render(nodes=self.node_indices.items(), parent_chains=parent_chains, constituents=constituents)

    @property
    def leaf_nodes(self):
        res = []
        for n in self.node_indices:
            if n._clones == []:
                res.append(n)
        return sorted(res, key=lambda n: self.node_indices[n])

    def get_parent_chain(self, node):
        chain = [self.node_indices[node]] + [self.node_indices[n] for n in node.parent_chain]
        #         assert node in self.nodes
        #         n = node
        #         chain = []
        #         while n:
        #             chain.append(self.nodes[n])
        #             n = n.parent
        return chain

    def get_constituents(self, node):
        assert node in self.node_indices
        return [self.node_indices[n] for n in node._constituents]