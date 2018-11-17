from mako.template import Template
import textwrap
from bidict import bidict, ValueDuplicationError


def is_anonymous(name):
    return name.startswith("ANONYMOUS_ANONYMOUS_ANONYMOUS_")


class TohuNamespaceError(Exception):
    """
    Custom exception.
    """


class TohuNamespace:

    def __init__(self):
        self.generators = bidict()

    def __repr__(self):
        s = Template(textwrap.dedent("""\
            <TohuNameSpace:
               %for name, g in items:
               ${name}: ${g}
               %endfor
            >
            """)).render(items=self.generators.items())
        return s

    def __len__(self):
        return len(self.generators)

    def __getitem__(self, key):
        return self.generators[key]

    def add_generator(self, g, name=None):
        if name is None:
            name = f"ANONYMOUS_ANONYMOUS_ANONYMOUS_{g.tohu_id}"

        if name in self.generators and self.generators[name] is not g:
            raise TohuNamespaceError("A different generator with the same name already exists.")

        try:
            self.generators[name] = g
        except ValueDuplicationError:
            existing_name = self.generators.inv[g]
            if is_anonymous(existing_name) and not is_anonymous(name):
                self.generators.inv[g] = name


    def add_generator_with_dependencies(self, g, name=None):
        self.add_generator(g, name=name)

        for c in g._input_generators:
            self.add_generator(c)