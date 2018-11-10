import pytest

from .context import tohu
from tohu.v5.primitive_generators import *


EXEMPLAR_GENERATORS = [
    Constant("quux"),
    Boolean(p=0.3),
]


@pytest.fixture
def exemplar_generators():
    """
    Return a list of generators which contains an example
    for each type of generator supported by tohu.
    """
    return EXEMPLAR_GENERATORS