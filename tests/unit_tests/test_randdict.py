# -*- coding: utf-8 -*-
"""
Tests for the RandDict class.
"""

from randdict import RandDict
from randdict.generators import Const, Sequential, Timestamp
from randdict.utils import MockRandomGenerator


class TestRandDict:
    """
    Unit tests for RandDict class.
    """

    def test_(self):
        """
        Check that calling RandDict.next() yields the expected sequence of random dictionaries.
        """
        randgen_offsets = MockRandomGenerator(values=[130, 45, 2000, 1639937, 0])
        timestamp_generator = Timestamp(start='2016-04-12 13:44', end=None, randgen_offsets=randgen_offsets)

        randdict = RandDict(foobar=Const(42), quux=Sequential(prefix='hello', digits=3), date=timestamp_generator)

        d1 = randdict.next()
        d2 = randdict.next()
        d3 = randdict.next()

        assert d1 == {'foobar': 42, 'quux': 'hello001', 'date': '2016-04-12 13:46:10'}
        assert d2 == {'foobar': 42, 'quux': 'hello002', 'date': '2016-04-12 13:44:45'}
        assert d3 == {'foobar': 42, 'quux': 'hello003', 'date': '2016-04-12 14:17:20'}
