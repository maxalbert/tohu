import pytest
import testing.postgresql
from datetime import datetime
from sqlalchemy import create_engine

from .context import tohu
from tohu import *


class QuuxGenerator(CustomGenerator):
    """
    Dummy generator for testing.
    """
    c = Sequential(prefix="quux_", digits=2)
    d = Float(7., 8.)
    e = Integer(low=3000, high=6000)
    f = TimestampNEW(start='2018-01-01', end='2018-01-02')


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

        quux_gen.generate(N=4, seed=12345).to_psql(conn.engine.url, table_name)

        result = conn.execute("SELECT * FROM {};".format(table_name))
        rows = result.fetchall()

        # Note: The floating point numbers returned from the Postgres DB
        #       have 1 digit less precision than the ones fed into it, so
        #       the last digit is rounded in the numbers below.
        rows_expected = [
            ('quux_01', 7.42994900933371, 5895, datetime(2018, 1, 2, 8, 42, 27)),
            ('quux_02', 7.13742091480008, 5318, datetime(2018, 1, 1, 3, 20, 18)),
            ('quux_03', 7.82030785493884, 4618, datetime(2018, 1, 1, 20, 8, 23)),
            ('quux_04', 7.1456803712148, 5606, datetime(2018, 1, 1, 0, 23, 29)),
            ]

        assert rows == rows_expected

    def test_append_to_existing_table(self, conn, quux_gen):
        # TODO: assert that quux_table doesn't exist yet.

        table_name = "quux_table_02"

        quux_gen.reset(seed=12345)
        quux_gen.generate(N=3).to_psql(conn.engine.url, table_name)
        quux_gen.generate(N=3).to_psql(conn.engine.url, table_name, if_exists='append')

        result = conn.execute("SELECT * FROM {};".format(table_name))
        rows = result.fetchall()

        # Note: The floating point numbers returned from the Postgres DB
        #       have 1 digit less precision than the ones fed into it, so
        #       the last digit is rounded in the numbers below.
        rows_expected = [
              ('quux_01', 7.42994900933371, 5895, datetime(2018, 1, 2, 8, 42, 27)),
              ('quux_02', 7.13742091480008, 5318, datetime(2018, 1, 1, 3, 20, 18)),
              ('quux_03', 7.82030785493884, 4618, datetime(2018, 1, 1, 20, 8, 23)),
              ('quux_04', 7.1456803712148, 5606, datetime(2018, 1, 1, 0, 23, 29)),
              ('quux_05', 7.45386523109212, 4918, datetime(2018, 1, 1, 4, 35, 25)),
              ('quux_06', 7.66254302016714, 3966, datetime(2018, 1, 1, 14, 43, 15)),
              ]


        assert rows == rows_expected
