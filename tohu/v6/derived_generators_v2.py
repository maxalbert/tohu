import datetime as dt

from .base import TohuBaseGenerator
from .primitive_generators import Constant
from .utils import TohuDateError, TohuTimestampError, ensure_is_date_object


def convert_to_date_object(date):
    if isinstance(date, Constant):
        return convert_to_date_object(date.value)
    else:
        try:
            return ensure_is_date_object(date)
        except TohuDateError:
            raise TohuDateError(f"Cannot convert input to (constant) date object: {date}")


def get_start_generator(start, date):
    if date is not None:
        date = convert_to_date_object(date)

    if start is None:
        start_value = dt.datetime(date.year, date.month, date.day)
        start_gen = Constant(start_value)
    elif isinstance(start, str):
        start_value = dt.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        start_gen = Constant(start_value)
    elif isinstance(start, Constant):
        return get_start_generator(start.value, date)
    else:
        raise NotImplementedError()

    return start_gen


def get_end_generator(end, date):
    if date is not None:
        date = convert_to_date_object(date)

    if end is None:
        end_value = dt.datetime(date.year, date.month, date.day, 23, 59, 59)
        end_gen = Constant(end_value)
    elif isinstance(end, str):
        end_value = dt.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        end_gen = Constant(end_value)
    elif isinstance(end, Constant):
        return get_start_generator(end.value, date)
    else:
        raise NotImplementedError()

    return end_gen


def get_start_end_end_generator(start, end, date):
    start_gen = get_start_generator(start, date)
    end_gen = get_end_generator(end, date)
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