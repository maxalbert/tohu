from .context import tohu
from tohu.v6.primitive_generators import Integer, TimestampPrimitive
from tohu.v6.derived_generators import IntegerDerived, Tee
from tohu.v6.derived_timestamp_generator import TimestampDerived
from tohu.v6.custom_generator import CustomGenerator


def test_tee_generator():

    class QuuxGenerator(CustomGenerator):
        aa = Integer(100, 200)
        bb = Integer(300, 400)
        cc = IntegerDerived(low=aa, high=bb)
        dd = Tee(cc, num=Integer(1, 8))

    g = QuuxGenerator()
    items = g.generate(100, seed=12345)
    df = items.to_df()

    def check_dd_is_between_aa_and_bb(row):
        return all([row.aa <= x <= row.bb for x in row.dd])

    dd_is_always_between_aa_and_bb = all(df.apply(check_dd_is_between_aa_and_bb, axis=1))
    assert True == dd_is_always_between_aa_and_bb


def test_tee_generator_v2():

    class QuuxGenerator(CustomGenerator):
        aa = Integer(100, 200)
        bb = Integer(300, 400)
        cc = Tee(IntegerDerived(low=aa, high=bb), num=Integer(1, 8))

    g = QuuxGenerator()
    items = g.generate(100, seed=12345)
    df = items.to_df()

    def check_cc_is_between_aa_and_bb(row):
        return all([row.aa <= x <= row.bb for x in row.cc])

    cc_is_always_between_aa_and_bb = all(df.apply(check_cc_is_between_aa_and_bb, axis=1))
    assert True == cc_is_always_between_aa_and_bb


def test_tee_generator_with_timestamps():
    """
    Regression test to ensure that Tee properly deals with timestamp generators that output their timestamps as strings.
    """

    class QuuxGenerator(CustomGenerator):
        aa = TimestampPrimitive(date="2018-01-01").strftime("%Y-%m-%d %H:%M:%S")
        bb = TimestampPrimitive(date="2018-01-02").strftime("%Y-%m-%d %H:%M:%S")
        cc = Tee(TimestampDerived(start=aa, end=bb).strftime("%Y-%m-%d %H:%M:%S"), num=Integer(1, 8))

    g = QuuxGenerator()
    items = g.generate(100, seed=12345)
    df = items.to_df()

    def check_cc_is_between_aa_and_bb(row):
        return all([row.aa <= x <= row.bb for x in row.cc])

    cc_is_always_between_aa_and_bb = all(df.apply(check_cc_is_between_aa_and_bb, axis=1))
    assert True == cc_is_always_between_aa_and_bb
