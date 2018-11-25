import pytest

from .context import tohu
from tohu.v6.primitive_generators import Integer, HashDigest, FakerGenerator
from tohu.v6.custom_generator import CustomGenerator
from .exemplar_generators.exemplar_custom_generators import Quux1Generator, Quux2Generator, Quux3Generator


@pytest.fixture(scope="module")
def quux_gen_1():
    return Quux1Generator()


@pytest.fixture(scope="module")
def quux_gen_2():
    return Quux2Generator(method="name")


@pytest.fixture(scope="module")
def quux_gen_3():
    return Quux3Generator(method="name")
