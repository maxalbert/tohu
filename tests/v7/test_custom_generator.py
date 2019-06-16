import pytest
from tohu.v7.primitive_generators import Integer, FakerGenerator, HashDigest
from tohu.v7.custom_generator import CustomGenerator


def test_make_custom_generator():
    #
    # Create empty custom generator.
    #
    g = CustomGenerator(tohu_items_name="Quux")
    assert g.field_names == []
    assert g.field_generators == {}

    #
    # Add field generators of different types.
    #
    aa = Integer(100, 200)
    g.add_field_generator("aa", aa)
    assert g.field_names == ["aa"]
    assert g.field_generators["aa"].is_clone_of(aa)
    assert g.tohu_items_cls.__name__ == "Quux"
    assert g.tohu_items_cls.field_names == ["aa"]

    bb = HashDigest(length=8)
    g.add_field_generator("bb", bb)
    assert g.field_names == ["aa", "bb"]
    assert g.field_generators["aa"].is_clone_of(aa)
    assert g.field_generators["bb"].is_clone_of(bb)
    assert g.tohu_items_cls.__name__ == "Quux"
    assert g.tohu_items_cls.field_names == ["aa", "bb"]

    cc = FakerGenerator(method="name")
    g.add_field_generator("cc", cc)
    assert g.field_names == ["aa", "bb", "cc"]
    assert g.field_generators["aa"].is_clone_of(aa)
    assert g.field_generators["bb"].is_clone_of(bb)
    assert g.field_generators["cc"].is_clone_of(cc)
    assert g.tohu_items_cls.__name__ == "Quux"
    assert g.tohu_items_cls.field_names == ["aa", "bb", "cc"]

    #
    # Check that the custom generator produces the expected items.
    #
    Quux = g.tohu_items_cls
    items_generated = g.generate(num=4, seed=99999)
    items_expected = [
        Quux(aa=104, bb="672EF2A4", cc="Calvin Peters"),
        Quux(aa=114, bb="2502048A", cc="Amanda Taylor"),
        Quux(aa=148, bb="679DAED2", cc="Amanda Barrett"),
        Quux(aa=126, bb="91554CC8", cc="Jesse Williams"),
    ]
    assert items_expected == items_generated


def test_custom_generator():
    class QuuxGenerator(CustomGenerator):
        aa = Integer(1, 7)
        bb = HashDigest(length=8)
        cc = FakerGenerator(method="name")
        dd = Integer(100, 200)

    g = QuuxGenerator()
    Quux = g.tohu_items_cls
    items_expected = [
        Quux(aa=1, bb="672EF2A4", cc="Calvin Peters", dd=181),
        Quux(aa=1, bb="2502048A", cc="Amanda Taylor", dd=139),
        Quux(aa=4, bb="679DAED2", cc="Amanda Barrett", dd=127),
        Quux(aa=2, bb="91554CC8", cc="Jesse Williams", dd=162),
        Quux(aa=5, bb="8EA713EA", cc="Rebecca Butler", dd=145),
    ]
    assert items_expected == g.generate(num=5, seed=99999)


def test_custom_generator_with_field_generator_defined_outside():
    aa = Integer(100, 200)
    cc = FakerGenerator(method="first_name")
    aa.reset(seed=11111)
    cc.reset(seed=22222)
    assert [163, 171, 142, 140, 121] == aa.generate(num=5)
    assert ['Joseph', 'Kevin', 'Carol', 'Jack', 'Robert'] == cc.generate(num=5)

    class QuuxGenerator(CustomGenerator):
        my_aa = aa
        my_bb = HashDigest(length=6)
        my_cc = cc

    g = QuuxGenerator()
    Quux = g.tohu_items_cls

    assert g.my_aa is aa
    assert g.my_bb is QuuxGenerator.my_bb
    assert g.my_cc is cc

    assert g.field_generators["my_aa"].is_clone_of(aa)
    assert g.field_generators["my_bb"].is_clone_of(QuuxGenerator.my_bb)
    assert g.field_generators["my_cc"].is_clone_of(cc)

    g.reset(seed=99999)
    items_expected = [
        Quux(my_aa=104, my_bb="672EF2", my_cc="Johnny"),
        Quux(my_aa=114, my_bb="250204", my_cc="David"),
        Quux(my_aa=148, my_bb="679DAE", my_cc="Angela"),
        Quux(my_aa=126, my_bb="91554C", my_cc="Pamela"),
        Quux(my_aa=177, my_bb="8EA713", my_cc="Blake"),
    ]
    assert items_expected == g.generate(num=5)

    g.reset(seed=99999)
    aa.reset(seed=11111)
    cc.reset(seed=22222)
    items_expected = [
        Quux(my_aa=163, my_bb='672EF2', my_cc='Joseph'),
        Quux(my_aa=171, my_bb='250204', my_cc='Kevin'),
        Quux(my_aa=142, my_bb='679DAE', my_cc='Carol'),
        Quux(my_aa=140, my_bb='91554C', my_cc='Jack'),
        Quux(my_aa=121, my_bb='8EA713', my_cc='Robert'),
    ]
    assert items_expected == g.generate(num=5)


def test_custom_generator_with_alias_for_existing_field_generator():
    class QuuxGenerator(CustomGenerator):
        aa = Integer(100, 200).set_tohu_name("aa")
        bb = aa

    g = QuuxGenerator()
    Quux = g.tohu_items_cls

    items_expected = [
        Quux(aa=120, bb=120),
        Quux(aa=122, bb=122),
        Quux(aa=197, bb=197),
        Quux(aa=140, bb=140),
        Quux(aa=184, bb=184),
    ]
    assert items_expected == g.generate(num=5, seed=66666)