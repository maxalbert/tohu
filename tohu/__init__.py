import logging

from .generators import *
from .custom_generator import CustomGenerator
from . import generators
from . import custom_generator

__all__ = generators.__all__ + custom_generator.__all__

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


#
# Create logger
#
logger = logging.getLogger('tohu')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('{asctime} {levelname}  {message}', datefmt='%Y-%m-%d %H:%M:%S', style='{')
ch.setFormatter(formatter)
logger.addHandler(ch)
