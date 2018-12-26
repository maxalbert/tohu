import datetime as dt

from tohu.v6.primitive_generators import Constant
from tohu.v6.derived_generators import Timestamp

from .common import NUM_PARAMS


class TimeTimestamp:

    params = NUM_PARAMS

    def setup(self, num):
        self.g1 = Constant(dt.datetime(2018, 1, 1, 11, 22, 33))
        self.g2 = Timestamp(start="2018-01-01 11:22:33", end="2018-01-01 11:22:33")
        self.g3 = Timestamp(start="2018-01-01 11:22:33", end="2018-05-23 14:15:16")

    def time_constant_timestamp(self, num):
        self.g1.generate(num=num)

    def time_timestamp_with_same_start_and_end(self, num):
        self.g2.generate(num=num)

    def time_general_timestamp(self, num):
        self.g3.generate(num=num)
