import datetime as dt
import pandas as pd

from .context import tohu
from tohu.v6.primitive_generators import Constant, Integer, HashDigest, FakerGenerator, TimestampPrimitive
from tohu.v6.derived_generators import Lookup, SelectMultiple
from tohu.v6.custom_generator import CustomGenerator
from .exemplar_generators.exemplar_custom_generators import *


def test_constituent_generator_templates(quux_gen_1, quux_gen_2, quux_gen_3, quux_gen_4):
    """
    Test that a couple of example custom generators contain the expected field generator templates.
    """
    constituent_generator_templates_expected_1 = {'aa': quux_gen_1.aa, 'bb': quux_gen_1.bb, 'cc': quux_gen_1.cc}
    constituent_generator_templates_expected_2 = {'dd': quux_gen_2.dd, 'ee': quux_gen_2.ee, 'ff': quux_gen_2.ff}
    constituent_generator_templates_expected_3 = {'xx': quux_gen_3.xx, 'yy': quux_gen_3.yy, 'zz': quux_gen_3.zz}
    constituent_generator_templates_expected_4 = {'aa': quux_gen_4.aa, 'bb': quux_gen_4.bb, 'cc': quux_gen_4.cc, 'dd': quux_gen_4.dd}

    assert constituent_generator_templates_expected_1 == quux_gen_1.ns_gens.named_generators
    assert constituent_generator_templates_expected_2 == quux_gen_2.ns_gens.named_generators
    assert constituent_generator_templates_expected_3 == quux_gen_3.ns_gens.named_generators
    assert constituent_generator_templates_expected_4 == quux_gen_4.ns_gens.named_generators


def test_constituent_generators(quux_gen_1, quux_gen_2, quux_gen_3, quux_gen_4):
    """
    Test that a couple of example custom generators contain field generators with the expected names and types.
    """
    assert quux_gen_1.ns_gens.names == ['aa', 'bb', 'cc']
    assert isinstance(quux_gen_1.ns_gens['aa'], Integer)
    assert isinstance(quux_gen_1.ns_gens['bb'], HashDigest)
    assert isinstance(quux_gen_1.ns_gens['cc'], FakerGenerator)

    assert quux_gen_2.ns_gens.names == ['dd', 'ee', 'ff']
    assert isinstance(quux_gen_2.ns_gens['dd'], Integer)
    assert isinstance(quux_gen_2.ns_gens['ee'], HashDigest)
    assert isinstance(quux_gen_2.ns_gens['ff'], FakerGenerator)

    assert quux_gen_3.ns_gens.names == ['xx', 'zz', 'yy']
    assert isinstance(quux_gen_3.ns_gens['xx'], Integer)
    assert isinstance(quux_gen_3.ns_gens['zz'], FakerGenerator)
    assert isinstance(quux_gen_3.ns_gens['yy'], HashDigest)

    assert quux_gen_4.ns_gens.names == ['aa', 'bb', 'cc', 'dd']
    assert isinstance(quux_gen_4.ns_gens['aa'], Constant)
    assert isinstance(quux_gen_4.ns_gens['bb'], HashDigest)
    assert isinstance(quux_gen_4.ns_gens['cc'], FakerGenerator)
    assert isinstance(quux_gen_4.ns_gens['dd'], Integer)


def test_field_names(quux_gen_1, quux_gen_2, quux_gen_3, quux_gen_4):
    """
    Test that a couple of example custom generators contain the expected field names.
    """
    assert ['aa', 'bb', 'cc'] == quux_gen_1.field_names
    assert ['dd', 'ee', 'ff'] == quux_gen_2.field_names
    assert ['xx', 'zz'] == quux_gen_3.field_names
    assert ['bb', 'dd', 'cc'] == quux_gen_4.field_names


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
    assert item4 == ('C851F707', 99, 'James Quux')

    # Double-check that the item class names are as expected
    assert "Quux1" == item1.__class__.__name__
    assert "Quux2" == item2.__class__.__name__
    assert "MyQuux3Item" == item3.__class__.__name__
    assert "Quux4" == item4.__class__.__name__


def test_generators_produce_items_with_fields_in_the_correct_order(quux_gen_1, quux_gen_2, quux_gen_3, quux_gen_4):
    item1 = next(quux_gen_1.reset(seed=11111))
    item2 = next(quux_gen_2.reset(seed=22222))
    item3 = next(quux_gen_3.reset(seed=33333))
    item4 = next(quux_gen_4.reset(seed=44444))

    # Check that fields are in the correct order
    assert item1 == (7, '7551AA72', 'Michelle Miller')
    assert item2 == (4, 'B0C4F475', 'April Henderson')
    assert item3 == (1, 'Erica Brown')
    assert item4 == ('6C02EEEC', 151, 'William Roberts')  # the order of the elements should reflect the order in quux_gen_4.__fields__


def test_compare_structure_of_two_custom_generators_with_complex_dependencies():
    """
    Test that custom generator with implicitly created internal generators produces same output as explicit one.
    """

    mapping = {
        1: ['a', 'aa', 'aaa', 'aaaa', 'aaaaa'],
        2: ['b', 'bb', 'bbb', 'bbbb', 'bbbbb'],
        3: ['c', 'cc', 'ccc', 'cccc', 'ccccc'],
        4: ['d', 'dd', 'ddd', 'dddd', 'ddddd'],
        5: ['e', 'ee', 'eee', 'eeee', 'eeeee'],
        6: ['f', 'ff', 'fff', 'ffff', 'fffff'],
        7: ['g', 'gg', 'ggg', 'gggg', 'ggggg'],
    }

    class Quux1Generator(CustomGenerator):
        nn = Integer(1, 5)
        aa = SelectMultiple(Lookup(Integer(1, 7), mapping), num=nn)

    class Quux2Generator(CustomGenerator):
        nn = Integer(1, 5)
        key_gen = Integer(1, 7)
        mapping_gen = Constant(mapping)
        lookup = Lookup(key_gen, mapping_gen)
        aa = SelectMultiple(lookup, num=nn)

    g1 = Quux1Generator()
    g2 = Quux2Generator()

    df1 = g1.generate(100, seed=12345).to_df()
    df2 = g2.generate(100, seed=12345).to_df()

    pd.util.testing.assert_frame_equal(df1, df2[["nn", "aa"]])


def test_references_by_name_creates_clones():

    class QuuxGenerator(CustomGenerator):
        a = Integer(100, 200)
        b = a
        c = a
        d = b

    g = QuuxGenerator()
    Quux = g.tohu_items_cls
    items = list(g.generate(5, seed=12345))

    expected_items = [
        Quux(a=118, b=118, c=118, d=118),
        Quux(a=192, b=192, c=192, d=192),
        Quux(a=192, b=192, c=192, d=192),
        Quux(a=196, b=196, c=196, d=196),
        Quux(a=135, b=135, c=135, d=135),
    ]

    assert expected_items == items


def test_clones_in_custom_generators():
    """
    Regression test to check that all properties of clones inside a custom generator are preserved.
    """

    # Previously there was a bug which meant that the string formatting
    # for generator 'bb' was not honoured correctly.
    class QuuxGenerator(CustomGenerator):
        aa = TimestampPrimitive(date="2018-01-01")
        bb = aa.strftime("%Y-%m-%d %H:%M:%S")

    g = QuuxGenerator()
    Quux = g.tohu_items_cls
    items = list(g.generate(num=5, seed=12345))

    items_expected = [
        Quux(aa=dt.datetime(2018, 1, 1, 5, 19, 55), bb='2018-01-01 05:19:55'),
        Quux(aa=dt.datetime(2018, 1, 1, 10, 2, 11), bb='2018-01-01 10:02:11'),
        Quux(aa=dt.datetime(2018, 1, 1, 1, 5, 28), bb='2018-01-01 01:05:28'),
        Quux(aa=dt.datetime(2018, 1, 1, 4, 57, 20), bb='2018-01-01 04:57:20'),
        Quux(aa=dt.datetime(2018, 1, 1, 19, 35, 26), bb='2018-01-01 19:35:26'),
    ]

    assert items_expected == items


def test_clones_without_explicit_parents_are_treated_correctly():
    """
    Test that custom generators containing clones whose parent is not
    an explicitly named generator produce the expected output items.
    """

    class QuuxGenerator(CustomGenerator):
        aa = TimestampPrimitive(date="2018-01-01").strftime("%Y-%m-%d %H:%M:%S")

    g = QuuxGenerator()
    Quux = g.tohu_items_cls
    items = list(g.generate(num=5, seed=12345))

    items_expected = [
        Quux(aa='2018-01-01 05:19:55'),
        Quux(aa='2018-01-01 10:02:11'),
        Quux(aa='2018-01-01 01:05:28'),
        Quux(aa='2018-01-01 04:57:20'),
        Quux(aa='2018-01-01 19:35:26'),
    ]

    assert items_expected == items


def test_instance_has_different_generators_than_class():

    class QuuxGenerator(CustomGenerator):
        aa = Integer(100, 200)
        bb = HashDigest(length=8)

    g = QuuxGenerator()

    assert g.aa is not QuuxGenerator.aa
    assert g.bb is not QuuxGenerator.bb