import pytest

from .context import tohu
from tohu.v6.primitive_generators import Integer, HashDigest, FakerGenerator
from .exemplar_generators.exemplar_custom_generators import *


def test_field_generator_templates(quux_gen_1, quux_gen_2, quux_gen_3):
    """
    Test that a couple of example custom generators contain the expected field generator templates.
    """
    field_generator_templates_expected_1 = {'aa': quux_gen_1.aa, 'bb': quux_gen_1.bb, 'cc': quux_gen_1.cc}
    field_generator_templates_expected_2 = {'aa': quux_gen_2.aa, 'bb': quux_gen_2.bb, 'cc': quux_gen_2.cc}
    field_generator_templates_expected_3 = {'aa': quux_gen_3.aa, 'bb': quux_gen_3.bb, 'cc': quux_gen_3.cc}

    assert field_generator_templates_expected_1 == quux_gen_1.field_generator_templates
    assert field_generator_templates_expected_2 == quux_gen_2.field_generator_templates
    assert field_generator_templates_expected_3 == quux_gen_3.field_generator_templates


def test_field_generators(quux_gen_1, quux_gen_2, quux_gen_3):
    """
    Test that a couple of example custom generators contain field generators with the expected names and types.
    """
    assert sorted(quux_gen_1.field_generators.keys()) == ['aa', 'bb', 'cc']
    assert isinstance(quux_gen_1.field_generators['aa'], Integer)
    assert isinstance(quux_gen_1.field_generators['bb'], HashDigest)
    assert isinstance(quux_gen_1.field_generators['cc'], FakerGenerator)

    assert sorted(quux_gen_2.field_generators.keys()) == ['aa', 'bb', 'cc']
    assert isinstance(quux_gen_2.field_generators['aa'], Integer)
    assert isinstance(quux_gen_2.field_generators['bb'], HashDigest)
    assert isinstance(quux_gen_2.field_generators['cc'], FakerGenerator)

    assert sorted(quux_gen_3.field_generators.keys()) == ['aa', 'bb', 'cc']
    assert isinstance(quux_gen_3.field_generators['aa'], Integer)
    assert isinstance(quux_gen_3.field_generators['bb'], HashDigest)
    assert isinstance(quux_gen_3.field_generators['cc'], FakerGenerator)


def test_field_names(quux_gen_1, quux_gen_2, quux_gen_3):
    """
    Test that a couple of example custom generators contain the expected field names.
    """
    assert ['aa', 'bb', 'cc'] == quux_gen_1.field_names
    assert ['aa', 'bb', 'cc'] == quux_gen_2.field_names
    assert ['aa', 'cc'] == quux_gen_3.field_names


def test_tohu_items_name(quux_gen_1, quux_gen_2, quux_gen_3):
    """
    Test that a couple of example custom generators contain the expected field names.
    """
    assert 'Quux1' == quux_gen_1.__tohu_items_name__
    assert 'Quux2' == quux_gen_2.__tohu_items_name__
    assert 'MyQuux3Item' == quux_gen_3.__tohu_items_name__
