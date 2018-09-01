import logging

#
# Create debug logger
#
logger = logging.getLogger('tohu-debug')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('{levelname}  {message}', datefmt='%Y-%m-%d %H:%M:%S', style='{')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel('DEBUG')


def debug_print_dict(d, name=None):
    if name is not None:
        logger.debug(f'{name}:')
    for name, gen in d.items():
        logger.debug(f'   {name}: {gen}')