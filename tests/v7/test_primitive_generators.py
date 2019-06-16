import pytest
from unittest.mock import Mock
from .context import tohu

from tohu.v7.primitive_generators import Constant, Boolean, FakerGenerator, HashDigest, Incremental, Integer


def test_constant():
    g = Constant("quux")
    expected_values = ["quux", "quux", "quux", "quux", "quux"]
    assert expected_values == g.generate(num=5, seed=99999)


def test_boolean():
    g = Boolean()
    expected_values = [True, True, False, True, True, True, False, True, True, True, False, True, False, True, False]
    assert expected_values == g.generate(num=15, seed=12345)

    g = Boolean(p=0.8)
    expected_values = [True, True, False, True, True, True, True, False, True, False, True, True, True, True, True]
    assert expected_values == g.generate(num=15, seed=99999)


def test_incremental():
    g = Incremental()
    expected_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert expected_values == g.generate(num=10, seed=99999)

    g = Incremental(start=200, step=4)
    expected_values = [200, 204, 208, 212, 216, 220, 224, 228, 232, 236]
    assert expected_values == g.generate(num=10, seed=99999)


def test_integer():
    g = Integer(low=100, high=200)
    expected_values = [102, 164, 118, 185, 182, 124, 149, 158, 100, 160]
    assert expected_values == g.generate(num=10, seed=12345)


def test_hashdigest():
    # Uppercase values (default)
    g = HashDigest(length=6)
    expected_values = ["E251FB", "E52DE1", "1DFDFD", "810876", "A44D15", "A9AD2D", "FE0F5E", "7E5191", "656D56"]
    assert expected_values == g.generate(num=9, seed=12345)

    # Lowercase values
    g = HashDigest(length=6, lowercase=True)
    expected_values = ["e251fb", "e52de1", "1dfdfd", "810876", "a44d15", "a9ad2d", "fe0f5e", "7e5191", "656d56"]
    assert expected_values == g.generate(num=9, seed=12345)

    # Raw bytes
    g = HashDigest(length=10, as_bytes=True)
    expected_values = [
        b"\xe2Q\xfb\xed\xe5-\xe1\xe3\x1d\xfd",
        b"\x81\x08v!\xa4M\x15/\xa9\xad",
        b"\xfe\x0f^4~Q\x91\xd3em",
        b'"B6\x88\x1d\x9eu\x98\x01\xbb',
        b"vl\xea\xf6q\xcd@v;\x9d",
    ]
    assert expected_values == g.generate(num=5, seed=12345)

    # Test that `length` must be even if the return value is a hex string (as opposed to raw bytes)
    with pytest.raises(ValueError, match="Length must be an even number if as_bytes=False"):
        HashDigest(length=5, as_bytes=False)


def test_faker_generator():
    g = FakerGenerator(method="name")
    expected_values = ["Eric Benton", "Heather Harris", "Thomas Obrien", "Amy Cook", "Kenneth Robles"]
    assert expected_values == g.generate(num=5, seed=99999)

    g = FakerGenerator(method="safe_color_name")
    expected_values = ["maroon", "olive", "white", "yellow", "purple"]
    assert expected_values == g.generate(num=5, seed=99999)


def test_calling_generate_with_and_without_seed():
    g = Constant("quux")
    g.reset = Mock()
    assert not g.reset.called

    # Calling generate() without seed should not call g.reset()
    g.generate(num=5, seed=None)
    assert not g.reset.called

    # Calling generate() with an explicit seed should call g.reset()
    g.generate(num=5, seed=11111)
    g.reset.assert_called_once_with(11111)
