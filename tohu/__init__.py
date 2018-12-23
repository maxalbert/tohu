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

from .v4.base import *
from .v4.primitive_generators import *
from .v4.derived_generators import *
from .v4.dispatch_generators import *
from .v4.custom_generator import CustomGenerator
from .v4.logging import logger
from .v4.utils import print_generated_sequence
from .v4 import base
from .v4 import primitive_generators
from .v4 import derived_generators
from .v4 import dispatch_generators
from .v4 import custom_generator
from .v4 import set_special_methods

__all__ = base.__all__ \
          + primitive_generators.__all__ \
          + derived_generators.__all__ \
          + dispatch_generators.__all__ \
          + custom_generator.__all__ \
          + ['tohu_logger', 'print_generated_sequence']

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

tohu_logger = logger  # alias