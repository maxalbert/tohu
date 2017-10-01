from .context import tohu
from tohu.generators import Integer, Float, Sequential, TupleGenerator
from tohu.utils import First, Second, Nth, BufferedTuple, Split, Zip


class DummyTupleGen(TupleGenerator):
    """
    Dummy generator class which generates a
    sequence of tuples with increasing counter.

    Example:

    >>> g = DummyTupleGen("Foo_", "Bar_", "Baz_", digits=1)
    >>> next(g)
    ("Foo_01", "Bar_01", "Baz_01")
    >>> next(g)
    ("Foo_02", "Bar_02", "Baz_02")
    >>> next(g)
    ("Foo_03", "Bar_03", "Baz_03")

    """
    def __init__(self, *prefixes):
        self.cnt = 0
        self.prefixes = prefixes
        self.tuple_len = len(prefixes)

    def __next__(self):
        self.cnt += 1
        return tuple(prefix + str(self.cnt) for prefix in self.prefixes)


class TestBufferedTuple:

    def test_tuple_elements_can_be_extracted_in_arbitrary_order(self):
        """
        Test that extracting individual tuple elements in
        arbitrary order produces the expected elements.
        """

        pair_gen = DummyTupleGen("Foo", "Bar")
        b = BufferedTuple(pair_gen)

        assert b.next_nth(0) == "Foo1"
        assert b.next_nth(1) == "Bar1"
        assert b.next_nth(0) == "Foo2"
        assert b.next_nth(0) == "Foo3"
        assert b.next_nth(1) == "Bar2"
        assert b.next_nth(0) == "Foo4"
        assert b.next_nth(1) == "Bar3"
        assert b.next_nth(1) == "Bar4"
        assert b.next_nth(1) == "Bar5"
        assert b.next_nth(1) == "Bar6"
        assert b.next_nth(0) == "Foo5"


class TestUtils:

    def test_extract_first_element_from_tuple_generator(self):
        """
        Test that `First` produces a generator yielding the first element in each tuple.
        """
        pairs = DummyTupleGen("a", "b")
        triples = DummyTupleGen("c", "d", "e")
        g = First(pairs)
        h = First(triples)
        assert list(g.generate(5)) == ["a1", "a2", "a3", "a4", "a5"]
        assert list(h.generate(3)) == ["c1", "c2", "c3"]

    def test_extract_second_element_from_tuple_generator(self):
        """
        Test that `Second` produces a generator yielding the second element in each tuple.
        """
        pairs = DummyTupleGen("a", "b")
        triples = DummyTupleGen("c", "d", "e")
        g = Second(pairs)
        h = Second(triples)
        assert list(g.generate(5)) == ["b1", "b2", "b3", "b4", "b5"]
        assert list(h.generate(3)) == ["d1", "d2", "d3"]

    def test_extract_nth_element_from_tuple_generator(self):
        """
        Test that `Nth` produces a generator yielding the n-th element in each tuple.
        """
        pairs = DummyTupleGen("a", "b")
        triples = DummyTupleGen("c", "d", "e")
        g = Nth(pairs, 0)
        h = Nth(triples, 2)
        assert list(g.generate(4)) == ["a1", "a2", "a3", "a4"]
        assert list(h.generate(3)) == ["e1", "e2", "e3"]

    def test_split_pairs(self):
        """
        Test that `Split` produces a generators yielding the individual elements
        in each tuple produced by the original generator
        """
        pairs = DummyTupleGen("Foo", "Quux")

        g, h = Split(pairs)

        assert next(g) == "Foo1"
        assert next(h) == "Quux1"
        assert next(g) == "Foo2"
        assert next(g) == "Foo3"
        assert next(g) == "Foo4"
        assert next(h) == "Quux2"
        assert next(h) == "Quux3"
        assert next(g) == "Foo5"
        assert next(h) == "Quux4"
        assert next(h) == "Quux5"
        assert next(h) == "Quux6"
        assert next(h) == "Quux7"
        assert next(g) == "Foo6"

    def test_split_triples(self):
        """
        Test that `Split` produces a generators yielding the individual elements
        in each tuple produced by the original generator
        """
        triples = DummyTupleGen("Foo", "Bar", "Quux")

        g1, g2, g3 = Split(triples)

        assert next(g1) == "Foo1"
        assert next(g2) == "Bar1"
        assert next(g3) == "Quux1"
        assert next(g1) == "Foo2"
        assert next(g1) == "Foo3"
        assert next(g1) == "Foo4"
        assert next(g3) == "Quux2"
        assert next(g1) == "Foo5"
        assert next(g2) == "Bar2"
        assert next(g2) == "Bar3"
        assert next(g3) == "Quux3"
        assert next(g3) == "Quux4"
        assert next(g3) == "Quux5"

    def test_zip(self):
        """

        """
        g1 = Sequential(prefix="Foo_", digits=3)
        g2 = Integer(0, 1000)
        g3 = Float(0, 1)

        g = Zip(g1, g2, g3, seed=99999)

        assert next(g) == ("Foo_001", 123, 0.12049047611259744)
        assert next(g) == ("Foo_002", 972, 0.3092850036925837)
        assert next(g) == ("Foo_003", 316, 0.9529198903583602)