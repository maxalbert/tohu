import pytest
from .context import tohu
from tohu.custom_generator import CustomGenerator
from tohu.generators import SelectOne, Integer, Float, Sequential, TupleGenerator, TohuBufferOverflow
from tohu.generators import First, Second, Nth, BufferedTuple, Split, Zip


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
        b = BufferedTuple(pair_gen, tuple_len=2)

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
        assert g.generate_NEW(5) == ["a1", "a2", "a3", "a4", "a5"]
        assert h.generate_NEW(3) == ["c1", "c2", "c3"]

    def test_extract_second_element_from_tuple_generator(self):
        """
        Test that `Second` produces a generator yielding the second element in each tuple.
        """
        pairs = DummyTupleGen("a", "b")
        triples = DummyTupleGen("c", "d", "e")
        g = Second(pairs)
        h = Second(triples)
        assert list(g.generate_NEW(5)) == ["b1", "b2", "b3", "b4", "b5"]
        assert list(h.generate_NEW(3)) == ["d1", "d2", "d3"]

    def test_extract_nth_element_from_tuple_generator(self):
        """
        Test that `Nth` produces a generator yielding the n-th element in each tuple.
        """
        pairs = DummyTupleGen("a", "b")
        triples = DummyTupleGen("c", "d", "e")
        g = Nth(pairs, 0)
        h = Nth(triples, 2)
        assert list(g.generate_NEW(4)) == ["a1", "a2", "a3", "a4"]
        assert list(h.generate_NEW(3)) == ["e1", "e2", "e3"]

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

    def test_split_output_of_SelectOne_generator(self):
        """
        Test that we can split the output of a SelectOne generator that produces tuples.
        """
        pairs = [('a', 1), ('b', 2), ('c', 3), ('d', 4)]
        g, h = Split(SelectOne(pairs, seed=99999), tuple_len=2)

        assert list(g.generate_NEW(N=5)) == ['a', 'c', 'b', 'c', 'd']
        assert list(h.generate_NEW(N=5)) == [1, 3, 2, 3, 4]

        g, h = Split(SelectOne(pairs, seed=99999), tuple_len=2)
        assert (next(g), next(h)) == ('a', 1)
        assert (next(g), next(h)) == ('c', 3)
        assert (next(g), next(h)) == ('b', 2)
        assert (next(g), next(h)) == ('c', 3)
        assert (next(g), next(h)) == ('d', 4)

    def test_zip(self):
        """
        """
        g1 = Sequential(prefix="Foo_", digits=3)
        g2 = Integer(0, 1000)
        g3 = Float(0, 1)

        g = Zip(g1, g2, g3, seed=99999)

        assert next(g) == ("Foo_001", 643, 0.2522927816477426)
        assert next(g) == ("Foo_002", 220, 0.1253337003482793)
        assert next(g) == ("Foo_003", 477, 0.554832836190999)

    def test_buffer_overflow(self):
        """
        Buffer overflow occurs when items from linked generators are not consumed at the same rate.
        """
        maxbuffer = 10

        pairs = [('AA', 'aa'), ('BB', 'bb'), ('CC', 'cc'), ('DD', 'dd'), ('EE', 'ee'), ('FF', 'ff')]
        x, y = Split(SelectOne(pairs), tuple_len=2, maxbuffer=maxbuffer)

        # This should work because we're only consuming `maxbuffer` elements
        x.reset(seed=12345)
        for _ in range(maxbuffer):
            next(x)

        # This should raise an error because we're consuming more than `maxbuffer` elements
        x.reset(seed=12345)
        with pytest.raises(TohuBufferOverflow):
            for _ in range(maxbuffer + 1):
                next(x)

    def test_split_generators_are_synced(self):
        """
        Split generators are synced (resetting one will also reset the other)
        """
        pairs = [('AA', 'aa'), ('BB', 'bb'), ('CC', 'cc'), ('DD', 'dd'), ('EE', 'ee'), ('FF', 'ff')]
        x, y = Split(SelectOne(pairs), tuple_len=2)

        x.reset(seed=12345)
        assert x.generate_NEW(5) == ['DD', 'FF', 'AA', 'CC', 'CC']
        assert y.generate_NEW(5) == ['dd', 'ff', 'aa', 'cc', 'cc']

        x.reset(seed=99999)
        assert x.generate_NEW(5) == ['AA', 'CC', 'EE', 'FF', 'FF']
        assert y.generate_NEW(5) == ['aa', 'cc', 'ee', 'ff', 'ff']

        y.reset(seed=12345)
        assert x.generate_NEW(5) == ['DD', 'FF', 'AA', 'CC', 'CC']
        assert y.generate_NEW(5) == ['dd', 'ff', 'aa', 'cc', 'cc']

    def test_split_generators_remain_in_sync_if_used_within_custom_generator(self):
        """
        Split generators remain in sync when created as attributes of a CustomGenerator
        """

        pairs = [('AA', 'aa'), ('BB', 'bb'), ('CC', 'cc'), ('DD', 'dd'), ('EE', 'ee'), ('FF', 'ff')]

        class QuuxGenerator(CustomGenerator):
            x, y = Split(SelectOne(pairs), tuple_len=2)

        g = QuuxGenerator()
        g.reset(seed=99999)
        assert next(g) == ('FF', 'ff')
        assert next(g) == ('BB', 'bb')
        assert next(g) == ('DD', 'dd')
        assert next(g) == ('CC', 'cc')
        assert next(g) == ('AA', 'aa')
        assert next(g) == ('CC', 'cc')
