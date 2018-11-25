from ..context import tohu
from tohu.v6.primitive_generators import *
from tohu.v6.custom_generator import CustomGenerator


class Quux1Generator(CustomGenerator):
    aa = Integer(1, 7)
    bb = HashDigest(length=8)
    cc = FakerGenerator(method="name")


class Quux2Generator(CustomGenerator):
    aa = Integer(1, 7)
    bb = HashDigest(length=8)

    def __init__(self, *, method):
        self.cc = FakerGenerator(method=method)
        super().__init__(method=method)


EXEMPLAR_CUSTOM_GENERATORS = [
    Quux1Generator(),
    Quux2Generator(method="name")
]
