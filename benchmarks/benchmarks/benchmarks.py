from tohu.v6.primitive_generators import Constant, Integer, HashDigest, FakerGenerator

NUM_PARAMS = [100, 100_000]


class TimeConstant:

    params = NUM_PARAMS

    def setup(self, num):
        self.g = Constant("foobar")

    def time_constant(self, num):
        self.g.generate(num=num)


class TimeInteger:

    params = NUM_PARAMS

    def setup(self, num):
        self.g = Integer(100, 200).reset(seed=99999)

    def time_integer(self, num):
        self.g.generate(num=num)


class TimeHashDigest:

    params = NUM_PARAMS

    def setup(self, num):
        self.g = HashDigest(length=8).reset(seed=99999)

    def time_hashdigest(self, num):
        self.g.generate(num=num)


class TimeFakerGenerator:

    params = NUM_PARAMS

    def setup(self, num):
        self.g = FakerGenerator(method="name").reset(seed=99999)

    def time_faker_generator(self, num):
        self.g.generate(num=num)