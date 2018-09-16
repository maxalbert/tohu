import logging
from operator import attrgetter

import numpy as np

from .base_NEW import TohuUltraBaseGenerator
from .generators_NEW import Constant, logger

__all__ = ['ExtractAttribute', 'Lookup', 'SelectOne']

logger = logging.getLogger('tohu')


class ExtractAttribute(TohuUltraBaseGenerator):
    """
    Generator which produces items that are attributes extracted from
    the items produced by a different generator.
    """

    def __init__(self, g, attr_name):
        logger.debug(f"Extracting attribute '{attr_name}' from parent={g}")
        self.parent = g
        self.gen = g.clone()
        self.attr_name = attr_name
        self.attrgetter = attrgetter(attr_name)

    def __repr__(self):
        return f"<ExtractAttribute '{self.attr_name}' from {self.parent} (id={id(self)}) >"

    def spawn(self, dependency_mapping):

        try:
            new_parent = dependency_mapping[self.parent]
        except KeyError:
            logger.warning(f'ExtractAttribute.spawn():')
            logger.warning(f'   self={self}')
            logger.warning(f'   dependency_mapping={dependency_mapping}')
            raise NotImplementedError("Cannot spawn ExtractAttribute because parent generator is not present in dependency mapping.")

        return ExtractAttribute(new_parent, self.attr_name)

    def clone(self):
        logger.debug('Cloning {self}')
        return ExtractAttribute(self.parent, self.attr_name)

    def __next__(self):
        return self.attrgetter(next(self.gen))

    def reset(self, seed):
        logger.debug(f"Ignoring explicit reset() on derived generator: {self}")

    def reset_clone(self, seed):
        logger.warning("TODO: rename method reset_clone() to reset_dependent_generator() because ExtractAttribute is not a direct clone")
        self.gen.reset(seed)


class Lookup(TohuUltraBaseGenerator):

    def __init__(self, g, mapping):
        self.parent = g
        self.gen = g.clone()
        self.mapping = mapping

    def __next__(self):
        return self.mapping[next(self.gen)]

    def spawn(self, dependency_mapping):
        try:
            new_parent = dependency_mapping[self.parent]
        except KeyError:
            logger.debug(f'While spawning {self}:')
            logger.debug(f'Could not find parent generator in dependency mapping. ')
            logger.debug(f'Using original parent: {self.parent}')
            logger.debug(f'Please check that this is ok.')
            new_parent = self.parent

        return Lookup(new_parent, self.mapping)

    def reset(self, seed):
        logger.debug(f"Ignoring explicit reset() on derived generator: {self}")

    def reset_clone(self, seed):
        logger.warning(
            "TODO: rename method reset_clone() to reset_dependent_generator() because Lookup is not a direct clone")
        self.gen.reset(seed)


class SelectOne(TohuUltraBaseGenerator):
    """
    Generator which produces a sequence of items taken from a given set of elements.
    """

    def __init__(self, values, p=None):
        """
        Parameters
        ----------
        values: list
            List of options from which to choose elements.
        p: list, optional
            The probabilities associated with each element in `values`.
            If not given the assumes a uniform distribution over all values.
        """
        self.orig_values = values
        self.parent = self.orig_values if isinstance(self.orig_values, TohuUltraBaseGenerator) else Constant(self.orig_values)
        self.gen = self.parent.clone()
        self.p = p
        self.randgen = np.random.RandomState()

    def spawn(self, dependency_mapping):

        if not isinstance(self.orig_values, TohuUltraBaseGenerator):
            new_values = self.orig_values
        else:
            try:
                # If the original `values` parameter was a tohu generator, check
                # if it was spawned before and if so use it as the new parent.
                new_values = dependency_mapping[self.parent]
            except KeyError:
                logger.debug(f'While spawning {self}:')
                logger.debug(f'Could not find parent generator in dependency mapping. ')
                logger.debug(f'Using original parent: {self.parent}')
                logger.debug(f'Please check that this is ok.')
                new_values = self.orig_values

        new_instance = SelectOne(new_values, p=self.p)
        new_instance.randgen.set_state(self.randgen.get_state())
        return new_instance

    def __getattr__(self, name):

        if name == '__isabstractmethod__':
            # Special case which is needed because TohuUltraBaseMeta is
            # derived from ABCMeta and it uses '__isabstractmethod__'
            # to check for abstract methods.
            #
            # TODO: This check should probably be moved to TohuUltraBaseGenerator somewhere.
            return

        if name == '_ipython_canary_method_should_not_exist_':
            # Special case which is needed because IPython uses this attribute internally.
            raise NotImplementedError("Special case needed for IPython")

        return ExtractAttribute(self, name)

    def __next__(self):
        """
        Return random element from the list of values provided during initialisation.
        """
        cur_values = next(self.gen)
        idx = self.randgen.choice(len(cur_values), p=self.p)
        return cur_values[idx]

    def reset(self, seed):
        logger.debug(f"Ignoring explicit reset() on derived generator: {self}")

    def reset_clone(self, seed):
        logger.warning("TODO: rename method reset_clone() to reset_dependent_generator() because ExtractAttribute is not a direct clone")
        if seed is not None:
            self.randgen.seed(seed)
            #self.gen.reset(seed)
        return self