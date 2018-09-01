import logging

logger = logging.getLogger('tohu')


class CustomGeneratorMetaV2(type):

    def __new__(metacls, cg_name, bases, clsdict):
        logger.debug('[DDD] CustomGeneratorMetaV2.__new__')
        logger.debug(f'         - metacls={metacls}')
        logger.debug(f'         - cg_name={cg_name}')
        logger.debug(f'         - bases={bases}')
        logger.debug(f'         - clsdict={clsdict}')

        new_obj = super(CustomGeneratorMetaV2, metacls).__new__(metacls, cg_name, bases, clsdict)
        logger.debug(f'         -- new_obj={new_obj}')

        def reset(self, seed=None):
            logger.debug(f'[EEE] Inside automatically generated reset() method for {self} (seed={seed})')

        new_obj.reset = reset

        return new_obj