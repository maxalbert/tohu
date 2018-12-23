from tohu.v6.primitive_generators import Integer, HashDigest, FakerGenerator
from tohu.v6.derived_generators import Apply, Lookup, SelectOne, SelectMultiple
from tohu.v6.custom_generator import CustomGenerator

from .common import NUM_PARAMS


mapping = {
    'A': ['a', 'aa', 'aaa', 'aaaa', 'aaaaa'],
    'B': ['b', 'bb', 'bbb', 'bbbb', 'bbbbb'],
    'C': ['c', 'cc', 'ccc', 'cccc', 'ccccc'],
    'D': ['d', 'dd', 'ddd', 'dddd', 'ddddd'],
    'E': ['e', 'ee', 'eee', 'eeee', 'eeeee'],
    'F': ['f', 'ff', 'fff', 'ffff', 'fffff'],
    'G': ['g', 'gg', 'ggg', 'gggg', 'ggggg'],
}

class Quux1Generator(CustomGenerator):
    aa = Integer(100, 200)
    bb = HashDigest(length=8)
    cc = FakerGenerator(method="name")


class Quux2Generator(CustomGenerator):
    aa = SelectOne(['A', 'B', 'C', 'D', 'E', 'F', 'G'])
    ll = Lookup(key=aa, mapping=mapping)
    nn = Integer(1, 5)
    bb = SelectMultiple(ll, num=nn)


class Quux3Generator(CustomGenerator):
    bb = SelectMultiple(Lookup(SelectOne(['A', 'B', 'C', 'D', 'E', 'F', 'G']), mapping), num=Integer(1, 5))


class TimeBasicCustomGenerator:

    params = NUM_PARAMS

    def setup(self, num):
        self.g1 = Quux1Generator()

    def time_basic_custom_generator(self, num):
        self.g1.generate(num=num)


class TimeComplexCustomGeneratorWithExplicitlyNamedFields:

    params = NUM_PARAMS

    def setup(self, num):
        self.g2 = Quux2Generator()

    def time_complex_custom_generator_with_explicitly_named_fields(self, num):
        self.g2.generate(num=num)


class TimeComplexCustomGeneratorWithAnonymousFields:
    params = NUM_PARAMS

    def setup(self, num):
        self.g3 = Quux3Generator()

    def time_complex_custom_generator_with_anonymous_fields(self, num):
        self.g3.generate(num=num)
