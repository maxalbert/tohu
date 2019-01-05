from distutils.version import StrictVersion
from platform import python_version

min_supported_python_version = '3.6'

if StrictVersion(python_version()) < StrictVersion(min_supported_python_version):
    error_msg = (
        "Tohu requires Python {min_supported_python_version} or greater to run "
        "(currently running under Python {python_version()})"
    )
    raise RuntimeError(error_msg)

from . import v6

from .v6.base import *
from .v6.primitive_generators import *
from .v6.derived_generators import *
from .v6.generator_dispatch import *
from .v6.custom_generator import CustomGenerator
from .v6.logging import logger
from .v6.utils import print_generated_sequence, print_tohu_version

from .v6 import base
from .v6 import primitive_generators
from .v6 import derived_generators
from .v6 import generator_dispatch
from .v6 import custom_generator
from .v6 import set_special_methods

__all__ = base.__all__ \
          + primitive_generators.__all__ \
          + derived_generators.__all__ \
          + generator_dispatch.__all__ \
          + custom_generator.__all__ \
          + ['tohu_logger', 'print_generated_sequence', 'print_tohu_version']

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

tohu_logger = logger  # alias