import pytest
from .exemplar_generators import EXEMPLAR_DERIVED_GENERATORS


@pytest.mark.parametrize("g", EXEMPLAR_DERIVED_GENERATORS)
def test_derived_generator_is_owner_of_its_constituent_generators(g):
    """
    """
    # Sanity check that list of constituent generators is not empty
    assert g.constituent_generators != []

    # Check that `g` is the owner of each of its constituent generators
    for c in g.constituent_generators:
        assert c.owner is g