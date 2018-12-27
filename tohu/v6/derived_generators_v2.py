import datetime as dt

from .base import TohuBaseGenerator
from .primitive_generators import Constant
from .utils import TohuTimestampError, ensure_is_date_object


def get_start_end_end_generator(start, end, date):
    if date is not None:
        date = ensure_is_date_object(date)

    if start is None:
        start_value = dt.datetime(date.year, date.month, date.day)
    else:
        start_value = dt.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")

    if end is None:
        end_value = dt.datetime(date.year, date.month, date.day, 23, 59, 59)
    else:
        end_value = dt.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

    start_gen = Constant(start_value)
    end_gen = Constant(end_value)
    return start_gen, end_gen


class TimestampDerived(TohuBaseGenerator):

    def __init__(self, start, end, date):
        self.start_gen, self.end_gen = get_start_end_end_generator(start, end, date)

    def __next__(self):
        pass

    def reset(self, seed):
        super().reset(seed)

    def spawn(self):
        pass

    def _set_random_state_from(self, other):
        pass