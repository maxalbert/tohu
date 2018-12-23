from tohu.v6.primitive_generators import Integer
from tohu.v6.derived_generators import Apply, Lookup, SelectOne, SelectMultiple

from .common import NUM_PARAMS


class TimeApply:

    params = NUM_PARAMS

    def setup(self, num):
        def add(x, y):
            return x + y

        self.g = Apply(add, Integer(100, 200), Integer(300, 400))

    def time_apply(self, num):
        self.g.generate(num=num)


class TimeLookup:

    params = NUM_PARAMS

    def setup(self, num):
        mapping = {1: 'aa', 2: 'bb', 3: 'cc', 4: 'dd', 5: 'ee'}
        self.g = Lookup(Integer(1, 5), mapping)

    def time_lookup(self, num):
        self.g.generate(num=num)


class TimeSelectOne:

    params = NUM_PARAMS

    def setup(self, num):
        self.g = SelectOne(['a', 'b', 'c', 'd', 'e'])

    def time_select_one(self, num):
        self.g.generate(num=num)


class TimeSelectMultiple:

    params = NUM_PARAMS

    def setup(self, num):
        self.g = SelectMultiple(['a', 'b', 'c', 'd', 'e'], num=Integer(1, 5))

    def time_select_multiple(self, num):
        self.g.generate(num=num)
