from .debugging import debug_print_dict, logger
from .generators import BaseGenerator


def add_generators(field_gens, dct):
    for name, gen in dct.items():
        if isinstance(gen, BaseGenerator):
            field_gens[name] = gen


def find_field_generators(obj):
    cls_dict = obj.__class__.__dict__
    obj_dict = obj.__dict__
    logger.debug(f'[FFF]')
    debug_print_dict(cls_dict, 'cls_dict')
    debug_print_dict(obj_dict, 'obj_dict')

    field_gens = {}
    add_generators(field_gens, cls_dict)
    add_generators(field_gens, obj_dict)

    #return {name: gen for name, gen in cls_and_inst_dict.items() if isinstance(gen, BaseGenerator)}
    return field_gens


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

        orig_init = new_obj.__init__

        def new_init(self, *args, **kwargs):
            # Call original __init__ function to ensure we pick up
            # any tohu generators that are defined there.
            orig_init(self, *args, **kwargs)

            # Find field generators
            self.field_gens = find_field_generators(self)
            logger.debug(f'Found {len(self.field_gens)} field generator(s):')
            debug_print_dict(self.field_gens)

        #
        # Create and assign automatically generated reset() method
        #

        def new_reset(self, seed=None):
            logger.debug(f'[EEE] Inside automatically generated reset() method for {self} (seed={seed})')
            logger.debug(f'      TODO: reset internal seed generator and call reset() on each child generator')

        new_obj.__init__ = new_init
        new_obj.reset = new_reset

        return new_obj