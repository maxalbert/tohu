from collections import namedtuple

from .context import tohu
from tohu.v6 import CustomGenerator, Integer, HashDigest, GetAttribute, SelectOne


class QuuxGenerator(CustomGenerator):
    """
    Helper class used in the tests below.
    """
    aa = Integer(100, 200)
    bb = HashDigest(length=8)

Quux = namedtuple("Quux", ["aa", "bb"])  # QuuxGenerator.tohu_items_cls


def test_getattribute_1():
    g = QuuxGenerator()
    a = GetAttribute(g, 'aa')
    b = GetAttribute(g, 'bb')

    g_items = list(g.generate(num=10, seed=12345))
    a_items = list(a.generate(num=10, seed=12345))
    b_items = list(b.generate(num=10, seed=12345))

    a_items_expected = [118, 192, 192, 196, 135, 193, 103, 117, 168, 154]
    b_items_expected = ['C851F707', '2553FCD0', 'CFF9005D', 'E9D2528C', 'EAB4D953', '5B9B84CA', '8B4519D3', '2E5251E2', '092E1890', '91AA24F1']

    assert a_items_expected == a_items == [x.aa for x in g_items]
    assert b_items_expected == b_items == [x.bb for x in g_items]


def test_getattribute_2():

    quux_items = QuuxGenerator().generate(num=100, seed=12345)

    class FoobarGenerator(CustomGenerator):
        cc = SelectOne(quux_items)
        dd = Integer(300, 400)

    g = FoobarGenerator()

    c = GetAttribute(g, 'cc')
    d = GetAttribute(g, 'dd')

    g_items = list(g.generate(num=10, seed=12345))
    c_items = list(c.generate(num=10, seed=12345))
    d_items = list(d.generate(num=10, seed=12345))

    c_items_expected = [
        Quux(aa=153, bb='1231B049'), Quux(aa=119, bb='AC558663'), Quux(aa=153, bb='033FAD81'), Quux(aa=170, bb='B2253864'),
        Quux(aa=189, bb='BB401018'), Quux(aa=163, bb='8F65D309'), Quux(aa=175, bb='792FD787'), Quux(aa=181, bb='9B3A8F09'),
        Quux(aa=117, bb='A8A0C21A'), Quux(aa=119, bb='56475250')]
    d_items_expected = [386, 333, 385, 307, 307, 343, 385, 356, 373, 368]

    assert c_items_expected == c_items == [x.cc for x in g_items]
    assert d_items_expected == d_items == [x.dd for x in g_items]


def test_getattribute_3():

    quux_gen = QuuxGenerator()
    quux_items = quux_gen.generate(num=100, seed=12345)

    g = SelectOne(quux_items)
    aa = GetAttribute(g, 'aa')
    bb = GetAttribute(g, 'bb')

    g_items = list(g.generate(num=10, seed=99999))
    aa_items = list(aa.generate(num=10, seed=99999))
    bb_items = list(bb.generate(num=10, seed=99999))

    aa_items_expected = [175, 140, 200, 190, 154, 144, 136, 150, 159, 163]
    bb_items_expected = ['33F14EBB', '8A2474D1', '6ABFF93D', '11D5D4D8', '746BD675', '75A313C9', 'B33ED5D1', 'BDD52BAE', '70963782', '8F65D309']

    assert aa_items == aa_items_expected == [x.aa for x in g_items]
    assert bb_items == bb_items_expected == [x.bb for x in g_items]


def test_getattribute_4():

    quux_gen = QuuxGenerator()
    quux_items = quux_gen.generate(num=100, seed=12345)

    g = SelectOne(quux_items)
    g_items = list(g.generate(num=10, seed=99999))
    aa_items = list(GetAttribute(g, 'aa').generate(num=10, seed=99999))
    bb_items = list(GetAttribute(g, 'bb').generate(num=10, seed=99999))

    aa_items_expected = [175, 140, 200, 190, 154, 144, 136, 150, 159, 163]
    bb_items_expected = ['33F14EBB', '8A2474D1', '6ABFF93D', '11D5D4D8', '746BD675', '75A313C9', 'B33ED5D1', 'BDD52BAE', '70963782', '8F65D309']

    assert aa_items_expected == aa_items == [x.aa for x in g_items]
    assert bb_items_expected == bb_items == [x.bb for x in g_items]
