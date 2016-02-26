import dateutil.parser
import pytest
import re
from .context import randdict
from randdict.generators import Const, DigitString, Empty, HashedID, Latitude, Longitude, PickFrom, RandIntString, RandRange, Sequential, Timestamp
from randdict.utils import MockRandomGenerator

# Number of repeats when checking random behaviour in tests.
NUM_REPEATS = 100


class TestConst:
    @pytest.mark.parametrize('value', ['foo', 'bar', -1, True, 33.412])
    def test_const_always_returns_the_same_value(self, value):
        """
        Check that calling `Const.next()` a bunch of times always returns the same value.
        """
        c = Const(value)

        for _ in range(NUM_REPEATS):
            assert c.next() == value


class TestEmpty:
    def test_emtpy_always_returns_the_empty_string(self):
        """
        Check that calling `next()` on an instance of type `Emtpy` always
        returns the empty string.

        """
        e = Empty()
        for _ in range(NUM_REPEATS):
            assert e.next() == ""


class TestSequential:
    def test_sequential_uses_name_argument_as_output_prefix(self):
        """
        Test that `Sequential` uses the `name` argument as the output prefix.
        """
        seq_foo = Sequential('Foo')
        assert seq_foo.next() == 'Foo0001'
        assert seq_foo.next() == 'Foo0002'

        seq_quux = Sequential('Quux')
        assert seq_quux.next() == 'Quux0001'
        assert seq_quux.next() == 'Quux0002'

    def test_sequential_honours_digits_argument(self):
        """
        Test that the `digits` argument can be used to control the number
        of digits in the output.
        """
        seq_foo = Sequential('Foo', digits=2)
        assert seq_foo.next() == 'Foo01'
        assert seq_foo.next() == 'Foo02'
        assert seq_foo.next() == 'Foo03'
        assert seq_foo.next() == 'Foo04'

        seq_bar = Sequential('Bar', digits=5)
        assert seq_bar.next() == 'Bar00001'
        assert seq_bar.next() == 'Bar00002'
        assert seq_bar.next() == 'Bar00003'
        assert seq_bar.next() == 'Bar00004'

    def test_sequential_can_be_called_and_returns_itself(self):
        """
        Test that calling an object of type `Sequential` returns the object
        itself. This is useful in tests where we use `Sequential` to mock
        other types of generators.

        """
        seq1 = Sequential('Foo')
        seq2 = Sequential('Bar')
        seq3 = Sequential('Quux')

        assert seq1() is seq1
        assert seq2() is seq2
        assert seq3() is seq3


class TestRandRange:
    @pytest.mark.parametrize('maxval', [1, 4, 9, 12])
    def test_rand_int_generates_random_integers_up_to_maxval(self, maxval):
        """
        Check that RandRange generates random integers 0 <= k < maxval
        when initialised as RandRange(maxval).

        """
        randgen = RandRange(maxval)

        for _ in range(NUM_REPEATS):
            value = randgen.next()
            assert isinstance(value, int)
            assert 0 <= value < maxval

    @pytest.mark.parametrize('minval, maxval', [(0, 1), (12, 14), (10004, 10008)])
    def test_rand_int_generates_random_integers_between_minval_and_maxval(self, minval, maxval):
        """
        Check that RandRange generates random integers minval <= k < maxval
        when initialised as RandRange(minval, maxval).

        """
        randgen = RandRange(minval, maxval)

        for _ in range(NUM_REPEATS):
            value = randgen.next()
            assert isinstance(value, int)
            assert minval <= value < maxval

    def test_setting_seed_leads_to_reproducible_output(self):
        """
        Check that calling seed() leads to reproducible output.
        """
        randrange = RandRange(0, 100000)

        for _ in range(NUM_REPEATS):
            randrange.seed(12)
            assert randrange.next() == 62202
            assert randrange.next() == 35257
            assert randrange.next() == 86176

    def test_calling_rand_range_with_more_than_two_arguments_raises_error(self):
        """
        Check that calling RandRange with more than two arguments raises an error.
        """
        with pytest.raises(ValueError):
            RandRange(0, 1, 2)



class TestRandIntString:
    @pytest.mark.parametrize('maxval', [1, 4, 9, 12])
    def test_rand_int_string_generates_strings_representing_random_integers_up_to_maxval(self, maxval):
        """
        Check that RandIntString generates strings representing random integers
        between 0 and maxval (inclusive) when initialised as RandIntString(maxval).

        """
        randgen = RandIntString(maxval)

        for _ in range(NUM_REPEATS):
            value = randgen.next()
            assert isinstance(value, str)
            assert 0 <= int(value) <= maxval

    @pytest.mark.parametrize('minval, maxval', [(0, 1), (15, 18), (44203, 44209)])
    def test_rand_int_string_generates_strings_representing_random_integers_between_minval_and_maxval(self, minval, maxval):
        """
        Check that RandIntString generates strings representing random
        integers between minval and maxval (both inclusive) when
        initialised as RandIntString(minval, maxval).

        """
        randgen = RandIntString(minval, maxval)

        for _ in range(NUM_REPEATS):
            value = randgen.next()
            assert isinstance(value, str)
            assert minval <= int(value) <= maxval

    def test_setting_seed_leads_to_reproducible_output(self):
        """
        Check that calling seed() leads to reproducible output.
        """
        randintstr = RandIntString(0, 100000)

        for _ in range(NUM_REPEATS):
            randintstr.seed(27)
            assert randintstr.next() == '84999'
            assert randintstr.next() == '62899'
            assert randintstr.next() == '91929'

    def test_calling_rand_int_string_with_more_than_two_arguments_raises_error(self):
        """
        Check that calling RandIntString with more than two arguments raises an error.
        """
        with pytest.raises(ValueError):
            RandIntString(0, 1, 2)


class TestLatitude:
    def test_latitude_generates_random_floats_in_correct_range(self):
        """
        Check that Latitude.next() returns strings represneting random floats between -90 and +90.
        """
        lat = Latitude()

        for _ in range(NUM_REPEATS):
            value = lat.next()
            assert isinstance(value, str)
            assert -90.0 <= float(value) <= 90.0

    def test_latitude_accepts_custom_random_number_generator(self):
        randgen = MockRandomGenerator(values=['40.123', '0.134', '-80.333', '12.993', '72.44'])
        lat = Latitude(randgen=randgen)

        assert lat.next() == '40.123'
        assert lat.next() == '0.134'
        assert lat.next() == '-80.333'
        assert lat.next() == '12.993'
        assert lat.next() == '72.44'

    def test_setting_seed_leads_to_reproducible_output(self):
        """
        Check that calling seed() leads to reproducible output.
        """
        lat = Latitude()

        for _ in range(NUM_REPEATS):
            lat.seed(88)
            assert lat.next() == '-18.45200214333765'
            assert lat.next() == '-55.887917429913216'
            assert lat.next() == '72.43907759559562'


class TestLongitude:
    def test_longitude_generates_random_floats_in_correct_range(self):
        """
        Check that Longitude.next() returns strings representing random floats between -180 and +180.
        """
        lon = Longitude()

        for _ in range(NUM_REPEATS):
            value = lon.next()
            assert isinstance(value, str)
            assert -180.0 <= float(value) <= 180.0

    def test_longitude_accepts_custom_random_number_generator(self):
        randgen = MockRandomGenerator(values=['20.44', '-179.1', '0.33', '20.17', '100.7'])
        lon = Longitude(randgen=randgen)

        assert lon.next() == '20.44'
        assert lon.next() == '-179.1'
        assert lon.next() == '0.33'
        assert lon.next() == '20.17'
        assert lon.next() == '100.7'

    def test_setting_seed_leads_to_reproducible_output(self):
        """
        Check that calling seed() leads to reproducible output.
        """
        lon = Longitude()

        for _ in range(NUM_REPEATS):
            lon.seed(133)
            assert lon.next() == '-2.2202458410340853'
            assert lon.next() == '-6.352591246081488'
            assert lon.next() == '96.82296202788018'


class TestTimestamp:
    def test_timestamp_generates_random_timestamps_in_the_correct_range(self):
        """
        Check that Timestamp.next() returns strings representing
        random timestamps in the correct date range.
        """
        start = '2016-04-12 13:44'
        end = '2016-04-12 18:57'
        start_date = dateutil.parser.parse(start)
        end_date = dateutil.parser.parse(end)

        ts = Timestamp(start=start, end=end)

        for _ in range(NUM_REPEATS):
            date = dateutil.parser.parse(ts.next())
            assert start_date <= date <= end_date

    def test_timestamp_accepts_custom_random_number_generator(self):
        """
        TODO: Write me!
        """
        randgen_offsets = MockRandomGenerator(values=[130, 45, 2000, 1639937, 0])
        ts = Timestamp(start='2016-04-12 13:44', end=None, randgen_offsets=randgen_offsets)

        assert ts.next() == '2016-04-12 13:46:10'
        assert ts.next() == '2016-04-12 13:44:45'
        assert ts.next() == '2016-04-12 14:17:20'
        assert ts.next() == '2016-05-01 13:16:17'
        assert ts.next() == '2016-04-12 13:44:00'

    def test_setting_seed_leads_to_reproducible_output(self):
        """
        Check that calling seed() leads to reproducible output.
        """
        ts = Timestamp(start='2016-04-12 13:44', end='2016-04-12 18:57')

        for _ in range(NUM_REPEATS):
            ts.seed(8892)
            assert ts.next() == '2016-04-12 16:05:38'
            assert ts.next() == '2016-04-12 14:43:17'
            assert ts.next() == '2016-04-12 16:03:26'

    def test_can_customize_output_format(self):
        """
        TODO: Write me!
        """
        randgen1 = MockRandomGenerator(values=[130, 45, 2000])
        randgen2 = MockRandomGenerator(values=[130, 45, 2000])
        randgen3 = MockRandomGenerator(values=[130, 45, 2000])
        ts1 = Timestamp(start='2016-04-12 13:44', randgen_offsets=randgen1, fmt='%m/%d/%y %H.%M')
        ts2 = Timestamp(start='2016-04-12 13:44', randgen_offsets=randgen2, fmt='%d-%b-%Y')
        ts3 = Timestamp(start='2016-04-12 13:44', randgen_offsets=randgen3, fmt='%Y-%b-%d', uppercase=True)

        assert ts1.next() == '04/12/16 13.46'
        assert ts1.next() == '04/12/16 13.44'
        assert ts1.next() == '04/12/16 14.17'

        assert ts2.next() == '12-Apr-2016'
        assert ts2.next() == '12-Apr-2016'
        assert ts2.next() == '12-Apr-2016'

        assert ts3.next() == '2016-APR-12'
        assert ts3.next() == '2016-APR-12'
        assert ts3.next() == '2016-APR-12'

    def test_timestamp_has_correct_total_number_of_seconds_between_start_and_end(self):
        """
        Regression test to check that the total number of seconds between start and end is correct.
        """
        ts = Timestamp(start='1988-01-05 12:45', end='2015-03-02 11:49')
        assert ts.dt == 856911840


class TestPickFrom:
    def test_pick_from_picks_random_elements_from_a_list_of_options(self):
        """
        Check that PickFrom.next() returns elements chosen from a given
        list of options.
        """
        values = ['foo', 42, True, 12.345]

        pick_from = PickFrom(values=values)

        for _ in range(NUM_REPEATS):
            val = pick_from.next()
            assert val in values

    def test_pick_from_accepts_custom_random_number_generator(self):
        """
        TODO: Write me!
        """
        randgen_indices = MockRandomGenerator(values=[0, 3, 3, 2, 0, 1, 4])
        pick_from = PickFrom(values=['foo', 42, True, 12.345, 'hello'],
                             randgen_indices=randgen_indices)

        assert pick_from.next() == 'foo'
        assert pick_from.next() == 12.345
        assert pick_from.next() == 12.345
        assert pick_from.next() is True
        assert pick_from.next() == 'foo'
        assert pick_from.next() == 42
        assert pick_from.next() == 'hello'

    def test_setting_seed_leads_to_reproducible_output(self):
        """
        Check that calling seed() leads to reproducible output.
        """
        pick_from = PickFrom(values=['foo', 42, True, 12.345, 'hello'])

        for _ in range(NUM_REPEATS):
            pick_from.seed(7330)
            assert pick_from.next() is True
            assert pick_from.next() == 'hello'
            assert pick_from.next() == 12.345
            assert pick_from.next() == 'foo'
            assert pick_from.next() is True
            assert pick_from.next() is True
            assert pick_from.next() == 42


class TestDigitString:
    digitpattern = re.compile('^[0-9]+$')

    def assert_produces_digit_strings(self, digitstr, minlength, maxlength):
        """
        Call `digitstr.next()` a bunch of times and check that the result is
        a digit string whose length is between `minlength` and `maxlength`.
        """
        for _ in range(NUM_REPEATS):
            s = digitstr.next()
            assert self.digitpattern.match(s) and (minlength <= len(s) <= maxlength)

    def test_digit_string_generates_string_of_expected_length(self):
        """
        Check that DigitString.next() returns random digit strings
        of the specified length.
        """
        digitstr1 = DigitString(length=6)
        digitstr2 = DigitString(length=32)
        digitstr3 = DigitString(minlength=8, maxlength=12)

        self.assert_produces_digit_strings(digitstr1, minlength=6, maxlength=6)
        self.assert_produces_digit_strings(digitstr2, minlength=32, maxlength=32)
        self.assert_produces_digit_strings(digitstr3, minlength=8, maxlength=12)

    def test_digit_string_accepts_custom_random_number_generators(self):
        """
        TODO: Write me!
        """
        randgen_lengths = MockRandomGenerator(values=[5, 3, 8])
        randgen_chars = MockRandomGenerator(
            values=['a', 'c', 'h', 'g', 'r',
                    'z', 'k', 'k',
                    'y', 't', 'g', 'p', 'x', 'e', 'w', 'g'])

        digitstr = DigitString(
            minlength=3, maxlength=8,
            rand_char_gen=randgen_chars,
            rand_length_gen=randgen_lengths,
        )

        assert digitstr.next() == 'achgr'
        assert digitstr.next() == 'zkk'
        assert digitstr.next() == 'ytgpxewg'

    def test_can_initialise_digit_string_with_maxlength_argument_only(self):
        """
        Check that DigitString can be initialised with `maxlength` only
        and that this implies minlength=1.
        """
        # The following should not raise an error
        digitstr = DigitString(maxlength=6)
        assert digitstr.minlength == 1
        assert digitstr.maxlength == 6

    def test_digit_string_raises_error_for_wrong_combination_of_length_arguments(self):
        """
        Check that an error is raised if `length` is specified in addition to
        one of `minlength`, `maxlength`, or if only one of the latter two is
        given.
        """
        with pytest.raises(ValueError):
            DigitString(length=4, minlength=4)

        with pytest.raises(ValueError):
            DigitString(length=6, maxlength=7)

        with pytest.raises(ValueError):
            DigitString(length=4, minlength=3, maxlength=12)

        with pytest.raises(ValueError):
            DigitString(minlength=4)

    def test_setting_seed_leads_to_reproducible_output(self):
        """
        Check that calling seed() leads to reproducible output.
        """
        digitstr = DigitString(maxlength=6)

        for _ in range(NUM_REPEATS):
            digitstr.seed(4444)
            assert digitstr.next() == '16'
            assert digitstr.next() == '646'
            assert digitstr.next() == '223801'
            assert digitstr.next() == '491373'


class TestHashedID:
    def test_setting_seed_leads_to_reproducible_output(self):
        """
        Check that calling seed() leads to reproducible output.
        """
        h = HashedID(length=10)

        for _ in range(NUM_REPEATS):
            h.seed(5555)
            assert h.next() == 'B58C7647AB'
            assert h.next() == '0BC3A343BA'
            assert h.next() == '47C3E28610'
            assert h.next() == 'D2A32DE319'
