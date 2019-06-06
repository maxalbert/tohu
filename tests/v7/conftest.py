import pytest
from .context import tohu
from tohu.v7.primitive_generators import Integer

# Note: importing from exemplar_generators triggers the check that each tohu
# generator class has an exemplar generator defined, so this import is useful
# even though we currently don't use EXEMPLAR_GENERATORS anywhere.
from .exemplar_generators import EXEMPLAR_GENERATORS


@pytest.fixture
def dummy_generator():
    """
    Return a dummy generator which can be usd in tests
    where the exact type of a generator doesn't matter.
    """
    return Integer(low=100, high=200)
