from .debugging import debug_print_dict, logger
from .generators import BaseGenerator, SeedGenerator

__all__ = ['CustomGeneratorMetaV2']


def add_field_generators(field_gens, dct):
    for name, gen in dct.items():
        if isinstance(gen, BaseGenerator):
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

        # Find field generator templates and attach spawned copies
        field_gens_templates = find_field_generators(self)
        logger.debug(f'Found {len(field_gens_templates)} field generator template(s):')
        debug_print_dict(field_gens_templates)

        logger.debug('Spawning field generator templates...')
        self.field_gens = {name: gen._spawn() for (name, gen) in field_gens_templates.items()}
        logger.debug(f'Field generatos attached to custom generator:')
        debug_print_dict(self.field_gens)

        # Add seed generator
        self.seed_generator = SeedGenerator()

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


class CustomGeneratorMetaV2(type):

    def __new__(metacls, cg_name, bases, clsdict):
        logger.debug('[DDD]')
        logger.debug('CustomGeneratorMetaV2.__new__')
        logger.debug(f'   - metacls={metacls}')
        logger.debug(f'   - cg_name={cg_name}')
        logger.debug(f'   - bases={bases}')
        logger.debug(f'   - clsdict={clsdict}')

        #
        # Create new custom generator object
        #
        new_obj = super(CustomGeneratorMetaV2, metacls).__new__(metacls, cg_name, bases, clsdict)
        logger.debug(f'   - new_obj={new_obj}')

        attach_new_init_method(new_obj)
        attach_new_reset_method(new_obj)

        return new_obj
