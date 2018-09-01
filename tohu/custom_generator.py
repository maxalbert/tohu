import attr
import pandas as pd
import re
from .base import UltraBaseGenerator, IndependentGenerator, DependentGenerator
from .cloning import CloneableMeta, ClonedGenerator
from .debugging import debug_print_dict, logger
from .generators import BaseGenerator, SeedGenerator

__all__ = ['CustomGenerator']


def add_field_generators(field_gens, dct):
    for name, gen in dct.items():
        if isinstance(gen, UltraBaseGenerator):
            field_gens[name] = gen


def find_field_generators(obj):
    """
    Return dictionary with the names and instances of
    all tohu.BaseGenerator occurring in the given
    object's class & instance namespaces.
    """

    cls_dict = obj.__class__.__dict__
    obj_dict = obj.__dict__
    logger.debug(f'[FFF]')
    debug_print_dict(cls_dict, 'cls_dict')
    debug_print_dict(obj_dict, 'obj_dict')

    field_gens = {}
    add_field_generators(field_gens, cls_dict)
    add_field_generators(field_gens, obj_dict)

    return field_gens


def set_item_class_name(cls_obj):
    """
    Return the first part of the class name of this custom generator.
    This will be used for the class name of the items produced by this
    generator.

    Examples:
        FoobarGenerator -> Foobar
        QuuxGenerator   -> Quux
    """
    if '__tohu__items__name__' in cls_obj.__dict__:
        logger.debug(f"Using item class name '{cls_obj.__tohu_items_name__}' (derived from attribute '__tohu_items_name__')")
    else:
        m = re.match('^(.*)Generator$', cls_obj.__name__)
        if m is not None:
            cls_obj.__tohu_items_name__ = m.group(1)
            logger.debug(f"Using item class name '{cls_obj.__tohu_items_name__}' (derived from custom generator name)")
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


def make_item_class_for_custom_generator(obj):
    """
    obj:
        The custom generator instance for which to create an item class
    """
    clsname = obj.__tohu_items_name__
    attr_names = obj.field_gens.keys()
    return make_item_class(clsname, attr_names)


def attach_new_init_method(obj):
    """
    Replace the existing obj.__init__() method with a new one
    which calls the original one and in addition performs the
    following actions:

    (1) Finds all instances of tohu.BaseGenerator in the namespace
        and collects them in the dictionary `self.field_gens`.
    (2) ..to do..
    """

    orig_init = obj.__init__

    def new_init(self, *args, **kwargs):
        # Call original __init__ function to ensure we pick up
        # any tohu generators that are defined there.
        orig_init(self, *args, **kwargs)

        #
        # Find field generator templates and attach spawned copies
        #
        field_gens_templates = find_field_generators(self)
        logger.debug(f'Found {len(field_gens_templates)} field generator template(s):')
        debug_print_dict(field_gens_templates)

        def find_orig_parent(dep_gen, origs):
            """
            Find name and instance of the parent of the dependent
            generator `dep_gen` amongst the generators in `origs`.
            """
            for parent_name, parent in origs.items():
                if dep_gen.parent is parent:
                    return parent_name, parent
            raise RuntimeError(f"Parent of dependent generator {dep_gen} not defined in the same custom generator")


        logger.debug('Spawning field generator templates...')
        origs = {}
        spawned = {}
        for name, gen in field_gens_templates.items():
            if isinstance(gen, IndependentGenerator) and gen in origs.values():
                logger.debug(f'Cloning generator {name}={gen} because it is an alias for an existing generator')
                gen = gen.clone()

            if isinstance(gen, IndependentGenerator):
                origs[name] = gen
                spawned[name] = gen._spawn()
            elif isinstance(gen, DependentGenerator):
                orig_parent_name, orig_parent = find_orig_parent(gen, origs)
                new_parent = spawned[orig_parent_name]
                #spawned[name] = new_parent.clone()
                spawned[name] = gen._spawn_and_reattach_parent(new_parent)
                logger.debug(f"Reattaching cloned generator {gen} to new parent {new_parent}")
            else:
                pass

        self.field_gens = spawned

        logger.debug(f'Field generators attached to custom generator:')
        debug_print_dict(self.field_gens)

        #
        # Add seed generator
        #
        self.seed_generator = SeedGenerator()

        #
        # Create class for the items produced by this generator
        #
        self.__class__.item_cls = make_item_class_for_custom_generator(self)

    obj.__init__ = new_init


def attach_new_reset_method(obj):
    """
    Attach a new `reset()` method to `obj` which resets the internal
    seed generator of `obj` and then resets each of its constituent
    field generators found in `obj.field_gens`.
    """

    #
    # Create and assign automatically generated reset() method
    #

    def new_reset(self, seed=None):
        logger.debug(f'[EEE] Inside automatically generated reset() method for {self} (seed={seed})')

        if seed is not None:
            self.seed_generator.reset(seed)
            for name, gen in self.field_gens.items():
                next_seed = next(self.seed_generator)
                logger.debug(f'Resetting field generator {name}={gen} with seed={next_seed}')
                gen.reset(next_seed)

        return self

    obj.reset = new_reset


def attach_new_next_method(obj):
    """
    TODO
    """

    def new_next(self):
        field_values = [next(g) for g in self.field_gens.values()]
        return self.item_cls(*field_values)

    obj.__next__ = new_next


def attach_new_spawn_method(obj):
    """
    TODO
    """

    def new_spawn(self):
        # TODO/FIXME: Check that this does the right thing:
        # (i) the spawned generator is independent of the original one (i.e. they can be reset independently without altering the other's behaviour)
        # (ii) ensure that it also works if this custom generator's __init__ requires additional arguments
        new_instance = self.__class__()
        return new_instance

    obj._spawn = new_spawn


class CustomGeneratorMeta(CloneableMeta):

    def __new__(metacls, cg_name, bases, clsdict):
        logger.debug('[DDD]')
        logger.debug('CustomGeneratorMeta.__new__')
        logger.debug(f'   - metacls={metacls}')
        logger.debug(f'   - cg_name={cg_name}')
        logger.debug(f'   - bases={bases}')
        logger.debug(f'   - clsdict={clsdict}')

        #
        # Create new custom generator object
        #
        new_obj = super(CustomGeneratorMeta, metacls).__new__(metacls, cg_name, bases, clsdict)
        logger.debug(f'   - new_obj={new_obj}')

        set_item_class_name(new_obj)
        attach_new_init_method(new_obj)
        attach_new_reset_method(new_obj)
        attach_new_next_method(new_obj)
        attach_new_spawn_method(new_obj)

        return new_obj


class CustomGenerator(BaseGenerator, metaclass=CustomGeneratorMeta):
    pass
