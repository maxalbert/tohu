import datetime as dt

from .base import TohuBaseGenerator
from .primitive_generators import Constant, DatePrimitive, TimestampPrimitive
from .utils import TohuDateError, TohuTimestampError, ensure_is_date_object


def convert_to_date_object(date):
    if isinstance(date, Constant):
        return convert_to_date_object(date.value)
    elif isinstance(date, DatePrimitive) and date.start == date.end:
        return date.start
    else:
        try:
            return ensure_is_date_object(date)
        except TohuDateError:
            raise TohuTimestampError(f"Argument 'date' must represent some kind of constant date object. Got: {date}")


def get_start_generator(start, date):
    if date is not None:
        date = convert_to_date_object(date)

    if start is None:
        start_value = dt.datetime(date.year, date.month, date.day)
        start_gen = Constant(start_value)
    elif isinstance(start, str):
        start_value = dt.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        start_gen = Constant(start_value)
    elif isinstance(start, dt.datetime):
        return Constant(start)
    elif isinstance(start, Constant):
        return get_start_generator(start.value, date)
    elif isinstance(start, TimestampPrimitive):
        return start
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
    elif isinstance(end, dt.datetime):
        return Constant(end)
    elif isinstance(end, Constant):
        return get_start_generator(end.value, date)
    elif isinstance(end, TimestampPrimitive):
        return end
    else:
        raise NotImplementedError()

    return end_gen


def get_start_end_end_generator(start, end, date):
    start_gen = get_start_generator(start, date)
    end_gen = get_end_generator(end, date)
    return start_gen, end_gen


def check_valid_inputs(start_gen, end_gen, date):
    if date is not None:
        date = convert_to_date_object(date)

    if isinstance(start_gen, TimestampPrimitive) and isinstance(end_gen, TimestampPrimitive):
        if start_gen.end > end_gen.start:
            raise TohuTimestampError(
                "Latest possible value of 'start' generator must not be after "
                "earliest possible value of 'end' generator."
            )

    if date is not None:
        if isinstance(start_gen, TimestampPrimitive):
            if not (start_gen.start.date() == date and start_gen.end.date() == date):
                raise TohuTimestampError(
                    "If the 'date' argument is given, all possible 'start' timestamp values must lie on that given date."
                )
        if isinstance(end_gen, TimestampPrimitive):
            if not (end_gen.start.date() == date and end_gen.end.date() == date):
                raise TohuTimestampError(
                    "If the 'date' argument is given, all possible 'end' timestamp values must lie on that given date."
                )


class TimestampDerived(TohuBaseGenerator):

    def __init__(self, *, start=None, end=None, date=None):
        super().__init__()

        if start is None and end is None and date is None:
            raise TohuTimestampError("Not all input arguments can be None.")
        if start is not None and end is not None and date is not None:
            raise TohuTimestampError("Arguments 'start', 'end', 'date' cannot all be provided.")

        self.start_gen, self.end_gen = get_start_end_end_generator(start, end, date)
        check_valid_inputs(self.start_gen, self.end_gen, date)

    def __next__(self):
        pass

    def reset(self, seed):
        super().reset(seed)

    def spawn(self):
        pass

    def _set_random_state_from(self, other):
        pass