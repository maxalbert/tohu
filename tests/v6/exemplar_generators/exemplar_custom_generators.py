from ..context import tohu
from tohu.v6.primitive_generators import *
from tohu.v6.custom_generator import CustomGenerator

__all__ = ['EXEMPLAR_CUSTOM_GENERATORS', 'Quux1Generator', 'Quux2Generator', 'Quux3Generator']


class Quux1Generator(CustomGenerator):
    aa = Integer(1, 7)
    bb = HashDigest(length=8)
    cc = FakerGenerator(method="name")


class Quux2Generator(CustomGenerator):
    dd = Integer(1, 7)
    ee = HashDigest(length=8)

    def __init__(self, *, method):
        self.ff = FakerGenerator(method=method)
        super().__init__(method=method)


class Quux3Generator(CustomGenerator):
    __tohu_items_name__ = 'MyQuux3Item'
    __fields__ = ['xx', 'zz']

    xx = Integer(1, 7)
    zz = FakerGenerator(method="name")

    def __init__(self, length):
        self.yy = HashDigest(length=length)
        super().__init__(length)


EXEMPLAR_CUSTOM_GENERATORS = [
    Quux1Generator(),
    Quux2Generator(method="name"),
    Quux3Generator(length=10),
]
