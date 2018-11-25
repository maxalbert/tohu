import pytest

from .context import tohu
from tohu.v6.primitive_generators import Constant, Integer, HashDigest, FakerGenerator
from .exemplar_generators.exemplar_custom_generators import *


def test_field_generator_templates(quux_gen_1, quux_gen_2, quux_gen_3, quux_gen_4):
    """
    Test that a couple of example custom generators contain the expected field generator templates.
    """
    field_generator_templates_expected_1 = {'aa': quux_gen_1.aa, 'bb': quux_gen_1.bb, 'cc': quux_gen_1.cc}
    field_generator_templates_expected_2 = {'dd': quux_gen_2.dd, 'ee': quux_gen_2.ee, 'ff': quux_gen_2.ff}
    field_generator_templates_expected_3 = {'xx': quux_gen_3.xx, 'yy': quux_gen_3.yy, 'zz': quux_gen_3.zz}
    field_generator_templates_expected_4 = {'aa': quux_gen_4.aa, 'bb': quux_gen_4.bb, 'cc': quux_gen_4.cc, 'dd': quux_gen_4.dd}

    assert field_generator_templates_expected_1 == quux_gen_1.field_generator_templates
    assert field_generator_templates_expected_2 == quux_gen_2.field_generator_templates
    assert field_generator_templates_expected_3 == quux_gen_3.field_generator_templates
    assert field_generator_templates_expected_4 == quux_gen_4.field_generator_templates


def test_field_generators(quux_gen_1, quux_gen_2, quux_gen_3, quux_gen_4):
    """
    Test that a couple of example custom generators contain field generators with the expected names and types.
    """
    assert list(quux_gen_1.field_generators.keys()) == ['aa', 'bb', 'cc']
    assert isinstance(quux_gen_1.field_generators['aa'], Integer)
    assert isinstance(quux_gen_1.field_generators['bb'], HashDigest)
    assert isinstance(quux_gen_1.field_generators['cc'], FakerGenerator)

    assert list(quux_gen_2.field_generators.keys()) == ['dd', 'ee', 'ff']
    assert isinstance(quux_gen_2.field_generators['dd'], Integer)
    assert isinstance(quux_gen_2.field_generators['ee'], HashDigest)
    assert isinstance(quux_gen_2.field_generators['ff'], FakerGenerator)

    assert list(quux_gen_3.field_generators.keys()) == ['xx', 'zz', 'yy']
    assert isinstance(quux_gen_3.field_generators['xx'], Integer)
    assert isinstance(quux_gen_3.field_generators['zz'], FakerGenerator)
    assert isinstance(quux_gen_3.field_generators['yy'], HashDigest)

    assert list(quux_gen_4.field_generators.keys()) == ['aa', 'bb', 'cc', 'dd']
    assert isinstance(quux_gen_4.field_generators['aa'], Constant)
    assert isinstance(quux_gen_4.field_generators['bb'], HashDigest)
    assert isinstance(quux_gen_4.field_generators['cc'], FakerGenerator)
    assert isinstance(quux_gen_4.field_generators['dd'], Integer)


def test_field_names(quux_gen_1, quux_gen_2, quux_gen_3, quux_gen_4):
    """
    Test that a couple of example custom generators contain the expected field names.
    """
    assert ['aa', 'bb', 'cc'] == quux_gen_1.field_names
    assert ['dd', 'ee', 'ff'] == quux_gen_2.field_names
    assert ['xx', 'zz'] == quux_gen_3.field_names
    assert ['dd', 'bb', 'cc'] == quux_gen_4.field_names


def test_tohu_items_name(quux_gen_1, quux_gen_2, quux_gen_3, quux_gen_4):
    """
    Test that a couple of example custom generators contain the expected field names.
    """
    assert 'Quux1' == quux_gen_1.__tohu_items_name__
    assert 'Quux2' == quux_gen_2.__tohu_items_name__
    assert 'MyQuux3Item' == quux_gen_3.__tohu_items_name__
    assert 'Quux4' == quux_gen_4.__tohu_items_name__


def test_different_instances_share_the_same_tohu_items_class():
    g1 = Quux1Generator()
    h1 = Quux1Generator()

    g2 = Quux2Generator(method="name")
    h2 = Quux2Generator(method="name")

    g3 = Quux3Generator(length=10)
    h3 = Quux3Generator(length=10)

    assert g1.tohu_items_cls is h1.tohu_items_cls
    assert g2.tohu_items_cls is h2.tohu_items_cls
    assert g3.tohu_items_cls is h3.tohu_items_cls

    assert g1.tohu_items_cls is not g2.tohu_items_cls
    assert g1.tohu_items_cls is not g3.tohu_items_cls
    assert g2.tohu_items_cls is not g3.tohu_items_cls


def test_tohu_items_can_be_initialised_with_expected_field_elements(quux_gen_1, quux_gen_2, quux_gen_3, quux_gen_4):
    # The following calls should succeed
    item1 = quux_gen_1.tohu_items_cls(aa=42, bb='C851F707', cc='Jane Dae')
    item2 = quux_gen_2.tohu_items_cls(dd=23, ee='C851F707', ff='John Doe')
    item3 = quux_gen_3.tohu_items_cls(xx=10, zz='Kate Foo')
    item4 = quux_gen_4.tohu_items_cls(dd=99, bb='C851F707', cc='James Quux')

    # Check that fields are in the correct order
    assert item1 == (42, 'C851F707', 'Jane Dae')
    assert item2 == (23, 'C851F707', 'John Doe')
    assert item3 == (10, 'Kate Foo')
    assert item4 == (99, 'C851F707', 'James Quux')

    # Double-check that the item class names are as expected
    assert "Quux1" == item1.__class__.__name__
    assert "Quux2" == item2.__class__.__name__
    assert "MyQuux3Item" == item3.__class__.__name__
    assert "Quux4" == item4.__class__.__name__
