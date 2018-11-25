import pytest

from .exemplar_generators.exemplar_custom_generators import *


@pytest.fixture(scope="module")
def quux_gen_1():
    return Quux1Generator()


@pytest.fixture(scope="module")
def quux_gen_2():
    return Quux2Generator(method="name")


@pytest.fixture(scope="module")
def quux_gen_3():
    return Quux3Generator(length=10)


@pytest.fixture(scope="module")
def quux_gen_4():
    return Quux4Generator()
