import logging
from .generators import BaseGenerator

logger = logging.getLogger('tohu')


def find_field_generators(obj):
    cls_dict = obj.__class__.__dict__
    inst_dict = obj.__dict__
    logger.debug(f'[FFF] cls_dict={cls_dict}')
    logger.debug(f'[FFF] inst_dict={inst_dict}')

    field_gens = {}

    for name, gen in cls_dict.items():
        if isinstance(gen, BaseGenerator):
            field_gens[name] = gen

    for name, gen in inst_dict.items():
        if isinstance(gen, BaseGenerator):
            field_gens[name] = gen

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

        #
        # Find field generators
        #
        field_gens = find_field_generators(new_obj)
        logger.debug(f'Found {len(field_gens)} field generator(s):')
        for name, gen in field_gens.items():
            logger.debug(f'   - {name}: {gen}')


        #
        # Create and assign automatically generated reset() method
        #

        def reset(self, seed=None):
            logger.debug(f'[EEE] Inside automatically generated reset() method for {self} (seed={seed})')
            logger.debug(f'      TODO: reset internal seed generator and call reset() on each child generator')

        new_obj.reset = reset

        return new_obj