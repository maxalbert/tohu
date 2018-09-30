import textwrap
from bidict import bidict

from .logging import logger
from .primitive_generators import PrimitiveGenerator
from .derived_generators import Apply, GetAttribute, Lookup, SelectOneFromGenerator

__all__ = ['SpawnContextCG']


class NoExistingSpawn(Exception):
    """
    Custom exception
    """


class SpawnContextCG:

    def __init__(self):
        self.templates = bidict()  # mapping {name -> field_generator_template}
        self.spawned = {}  # mapping {name -> field_generator}
        self.anonymous = []  # names of anonymously spawned generators

    def __repr__(self):
        return textwrap.dedent(f"""
            <SpawnContextCG:
                templates: {dict(self.templates)}
                spawned:   {dict(self.spawned)}
                anonymous: {self.anonymous}
            >""")

    @property
    def nonanonymous_spawns(self):
        return {name: g for (name, g) in self.spawned.items() if name not in self.anonymous}

    def get_existing_spawn(self, g_tpl):
        try:
            existing_name = self.templates.inv[g_tpl]
            return self.spawned[existing_name]
        except KeyError:
            logger.debug(f"No existing spawn for {g_tpl}")
            raise NoExistingSpawn()

    def spawn_template(self, g_tpl, *, name):
        if name is None:
            try:
                name = self.templates.inv[g_tpl]
            except KeyError:
                name = f'anonymous_{g_tpl.tohu_id}'
                self.anonymous.append(name)
                logger.debug(f"Found anonymous field generator template: {g_tpl}")

        try:
            self.spawned[name] = self.get_existing_spawn(g_tpl)
        except NoExistingSpawn:
            if isinstance(g_tpl, PrimitiveGenerator):
                self.templates[name] = g_tpl
                self.spawned[name] = g_tpl.spawn()
            elif isinstance(g_tpl, SelectOneFromGenerator):
                new_parent = self.spawn_template(g_tpl.parent, name=None)
                self.templates[name] = g_tpl
                self.spawned[name] = SelectOneFromGenerator(new_parent)
            elif isinstance(g_tpl, GetAttribute):
                new_parent = self.spawn_template(g_tpl.parent, name=None)
                self.templates[name] = g_tpl
                self.spawned[name] = GetAttribute(new_parent, name=g_tpl.name)
            elif isinstance(g_tpl, Lookup):
                new_parent = self.spawn_template(g_tpl.parent, name=None)
                self.templates[name] = g_tpl
                self.spawned[name] = Lookup(new_parent, mapping=g_tpl.mapping)
            elif isinstance(g_tpl, Apply):
                new_arg_gens = []
                for gen in g_tpl.func_arg_gens_orig.arg_gens:
                    new_arg_gens.append(self.spawn_template(gen, name=None))

                new_kwarg_gens = {}
                for gen_name, gen in g_tpl.func_arg_gens_orig.kwarg_gens.items():
                    new_kwarg_gens[gen_name] = self.spawn_template(gen, name=None)

                self.templates[name] = g_tpl
                self.spawned[name] = Apply(g_tpl.func, *new_arg_gens, **new_kwarg_gens)
            else:
                raise NotImplementedError(f'g_tpl: {g_tpl}')

        self.spawned[name].set_tohu_name(name)  # set tohu_name for nicer debugging

        return self.spawned[name]


