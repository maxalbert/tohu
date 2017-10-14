import pytest
import testing.postgresql
from sqlalchemy import create_engine

from .context import tohu
from tohu import *


class QuuxGenerator(CustomGenerator):
    """
    Dummy generator for testing.
    """
    c = Sequential(prefix="quux_", digits=2)
    d = Float(7., 8.)
    e = Integer(lo=3000, hi=6000)


@pytest.fixture(scope="module")
def conn():
    postgresql = testing.postgresql.Postgresql()
    engine = create_engine(postgresql.url())
    conn = engine.connect()

    yield conn

    conn.close()


@pytest.fixture(autouse=True)
def quux_gen():
    return QuuxGenerator()


class TestPostgreSQLExport:

    def test_export_to_new_table(self, conn, quux_gen):
        # TODO: assert that quux_table doesn't exist yet.

        table_name = "quux_table_01"

        quux_gen.to_psql(conn.engine.url, table_name, N=4, seed=12345)

        result = conn.execute("SELECT * FROM {};".format(table_name))
        rows = result.fetchall()

        # Note: The floating point numbers returned from the Postgres DB
        #       have 1 digit less precision than the ones fed into it, so
        #       the last digit is rounded in the numbers below.
        rows_expected = [
            ('quux_01', 7.03257635527289, 4001),
            ('quux_02', 7.89341487598482, 5032),
            ('quux_03', 7.62755549311908, 5198),
            ('quux_04', 7.33267215551471, 4866)
        ]

        assert rows == rows_expected

    def test_append_to_existing_table(self, conn, quux_gen):
        # TODO: assert that quux_table doesn't exist yet.

        table_name = "quux_table_02"

        quux_gen.reset(seed=12345)
        quux_gen.to_psql(conn.engine.url, table_name, N=3)
        quux_gen.to_psql(conn.engine.url, table_name, N=3, if_exists='append')

        result = conn.execute("SELECT * FROM {};".format(table_name))
        rows = result.fetchall()

        # Note: The floating point numbers returned from the Postgres DB
        #       have 1 digit less precision than the ones fed into it, so
        #       the last digit is rounded in the numbers below.
        rows_expected = [
            ('quux_01', 7.03257635527289, 4001),
            ('quux_02', 7.89341487598482, 5032),
            ('quux_03', 7.62755549311908, 5198),

            ('quux_04', 7.33267215551471, 4866),
            ('quux_05', 7.5320838389968, 3040),
            ('quux_06', 7.49229751296052, 5229),
        ]

        assert rows == rows_expected
