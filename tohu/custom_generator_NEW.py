import attr
import logging
import pandas as pd
import re
from .base_NEW import SeedGenerator, TohuUltraBaseGenerator, TohuUltraBaseMeta
#from .debugging import debug_print_dict

__all__ = ['CustomGenerator', 'CustomGeneratorMeta']

logger = logging.getLogger('tohu')


# TODO: This is copied from debugging.py to avoid having to import it because it uses the existing BaseGenerator class.
#       Remove this implementation once the current refactoring is complete.
def debug_print_dict(d, name=None):
    if name is not None:
        logger.debug(f'{name}:')
    for name, gen in d.items():
        logger.debug(f'   {name}: {gen}')


def update_with_tohu_generators(field_gens, adict):
    """
    Helper function which updates `field_gens` with any items in the
    dictionary `adict` that are instances of `TohuUltraBaseGenerator`.
    """
    for name, gen in adict.items():
        if isinstance(gen, TohuUltraBaseGenerator):
            field_gens[name] = gen


def find_field_generator_templates(obj):
    """
    Return dictionary with the names and instances of
    all tohu.BaseGenerator occurring in the given
    object's class & instance namespaces.
    """

    cls_dict = obj.__class__.__dict__
    obj_dict = obj.__dict__
    #debug_print_dict(cls_dict, 'cls_dict')
    #debug_print_dict(obj_dict, 'obj_dict')

    field_gens = {}
    update_with_tohu_generators(field_gens, cls_dict)
    update_with_tohu_generators(field_gens, obj_dict)

    return field_gens


def set_item_class_name_on_custom_generator_class(cls):
    """
    Set the attribute `cls.__tohu_items_name__` to a string which defines the name
    of the namedtuple class which will be used to produce items for the custom
    generator.

    By default this will be the first part of the class name (before '...Generator'),
    for example:

        FoobarGenerator -> Foobar
        QuuxGenerator   -> Quux

    However, it can be set explicitly by the user by defining `__tohu_items_name__`
    in the class definition, for example:

        class Quux(CustomGenerator):
            __tohu_items_name__ = 'MyQuuxItem'
    """
    if '__tohu__items__name__' in cls.__dict__:
        logger.debug(
            f"Using item class name '{cls.__tohu_items_name__}' (derived from attribute '__tohu_items_name__')")
    else:
        m = re.match('^(.*)Generator$', cls.__name__)
        if m is not None:
            cls.__tohu_items_name__ = m.group(1)
            logger.debug(f"Using item class name '{cls.__tohu_items_name__}' (derived from custom generator name)")
        else:
            raise ValueError("Cannot derive class name for items to be produced by custom generator. "
                             "Please set '__tohu_items_name__' at the top of the custom generator's "
                             "definition or change its name so that it ends in '...Generator'")


def make_item_class(clsname, attr_names):
    """
    Parameters
    ----------
    clsname: string
        Name of the class to be created

    attr_names: list of strings
        Names of the attributes of the class to be created
    """

    item_cls = attr.make_class(clsname, {name: attr.ib() for name in attr_names}, repr=False, cmp=True)

    def new_repr(self):
        all_fields = ', '.join([f'{name}={repr(value)}' for name, value in attr.asdict(self).items()])
        return f'{clsname}({all_fields})'

    orig_eq = item_cls.__eq__

    def new_eq(self, other):
        """
        Custom __eq__() method which also allows comparisons with
        tuples and dictionaries. This is mostly for convenience
        during testing.
        """

        if isinstance(other, self.__class__):
            return orig_eq(self, other)
        else:
            if isinstance(other, tuple):
                return attr.astuple(self) == other
            elif isinstance(other, dict):
                return attr.asdict(self) == other
            else:
                return NotImplemented

    item_cls.__repr__ = new_repr
    item_cls.__eq__ = new_eq
    item_cls.keys = lambda self: attr_names
    item_cls.__getitem__ = lambda self, key: getattr(self, key)
    item_cls.as_dict = lambda self: attr.asdict(self)
    item_cls.to_series = lambda self: pd.Series(attr.asdict(self))

    return item_cls


def make_item_class_for_custom_generator_class(cls):
    """
    cls:
        The custom generator class for which to create an item-class
    """
    clsname = cls.__tohu_items_name__
    attr_names = cls.field_gens.keys()
    return make_item_class(clsname, attr_names)


def _add_new_init_method(cls):
    """
    Replace the existing cls.__init__() method with a new one
    which calls the original one and in addition performs the
    following actions:

    (1) Finds all instances of tohu.BaseGenerator in the namespace
        and collects them in the dictionary `self.field_gens`.
    (2) ..to do..
    """

    orig_init = cls.__init__

    def new_init_method(self, *args, **kwargs):
        logger.debug(f"Initialising new {self} (type: {type(self)})")

        # Call original __init__ function to ensure we pick up
        # any tohu generators that are defined there.
        #
        logger.debug(f"    orig_init: {orig_init}")
        orig_init(self, *args, **kwargs)

        #
        # Find field generator templates and spawn them to create
        # field generators for the new custom generator instance.
        #
        field_gens_templates = find_field_generator_templates(self)
        logger.debug(f'Found {len(field_gens_templates)} field generator template(s):')
        debug_print_dict(field_gens_templates)

        logger.debug('Spawning field generator templates...')
        origs = {}
        spawned = {}
        dependency_mapping = {}
        for (name, gen) in field_gens_templates.items():
            origs[name] = gen
            spawned[name] = gen.spawn(dependency_mapping)
            dependency_mapping[gen] = spawned[name]
            logger.debug(f'Adding dependency mapping: {gen} -> {spawned[name]}')

        self.field_gens = spawned
        self.__dict__.update(self.field_gens)

        logger.debug(f'Spawned field generators attached to custom generator instance:')
        debug_print_dict(self.field_gens)

        # Add seed generator
        #
        #self.seed_generator = SeedGenerator()

        # Create class for the items produced by this generator
        #
        self.__class__.item_cls = make_item_class_for_custom_generator_class(self)

    cls.__init__ = new_init_method


def _add_new_next_method(cls):
    """
    TODO
    """

    def new_next(self):
        field_values = [next(g) for g in self.field_gens.values()]
        return self.item_cls(*field_values)

    cls.__next__ = new_next


def _add_new_reset_method(cls):
    """
    Attach a new `reset()` method to `cls` which resets the internal
    seed generator of `cls` and then resets each of its constituent
    field generators found in `cls.field_gens`.
    """

    #
    # Create and assign automatically generated reset() method
    #


    def new_reset_method(self, seed=None):
        logger.debug(f'[EEE] Inside automatically generated reset() method for {self} (seed={seed})')

        if seed is not None:
            self.seed_generator.reset(seed)
            for name, gen in self.field_gens.items():
                next_seed = next(self.seed_generator)
                gen.reset(next_seed)

            # TODO: the following should be covered by the newly added
            # reset() method in IndependentGeneratorMeta. However, for
            # some reason we can't call this via the usual `orig_reset()`
            # pattern, so we have to duplicate this here. Not ideal...
            for c in self._clones:
                c.reset_clone(seed)

        return self

    cls.reset = new_reset_method


def _add_new_spawn_method(cls):
    """
    TODO
    """

    def new_spawn_method(self, dependency_mapping):
        # TODO/FIXME: Check that this does the right thing:
        # (i) the spawned generator is independent of the original one (i.e. they can be reset independently without altering the other's behaviour)
        # (ii) ensure that it also works if this custom generator's __init__ requires additional arguments
        #new_instance = self.__class__()
        #
        # FIXME: It would be good to explicitly spawn the field generators of `self`
        #        here because this would ensure that the internal random generators
        #        of the spawned versions are in the same state as the ones in `self`.
        #        This would guarantee that the spawned custom generator produces the
        #        same elements as `self` even before reset() is called explicitly.
        new_instance = cls()
        return new_instance

    cls.spawn = new_spawn_method


class CustomGeneratorMeta(TohuUltraBaseMeta):

    def __new__(metacls, cg_name, bases, clsdict):
        #
        # Create new custom generator class
        #
        new_cls = super(CustomGeneratorMeta, metacls).__new__(metacls, cg_name, bases, clsdict)
        logger.debug('Inside CustomGeneratorMeta.__new__')
        # logger.debug(f'   - metacls={metacls}')
        # logger.debug(f'   - cg_name={cg_name}')
        # logger.debug(f'   - bases={bases}')
        # logger.debug(f'   - clsdict={clsdict}')
        logger.debug(f'   - new_cls={new_cls} (type: {type(new_cls)})')

        set_item_class_name_on_custom_generator_class(new_cls)
        _add_new_init_method(new_cls)
        _add_new_reset_method(new_cls)
        _add_new_next_method(new_cls)
        _add_new_spawn_method(new_cls)

        return new_cls


class CustomGenerator(TohuUltraBaseGenerator, metaclass=CustomGeneratorMeta):

    def __init__(self):
        logger.debug("[DDD] Inside __init__ of CustomGenerator (which is a no-op)")