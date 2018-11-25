from ..context import tohu
from tohu.v6.primitive_generators import *
from tohu.v6.custom_generator import CustomGenerator

__all__ = ['EXEMPLAR_CUSTOM_GENERATORS', 'Quux1Generator', 'Quux2Generator', 'Quux3Generator', 'Quux4Generator']


class Quux1Generator(CustomGenerator):
    """
    Basic custom generator with all field generators defined on the class.
    """
    aa = Integer(1, 7)
    bb = HashDigest(length=8)
    cc = FakerGenerator(method="name")


class Quux2Generator(CustomGenerator):
    """
    Custom generator with one field generator defined dynamically in __init__.
    """
    dd = Integer(1, 7)
    ee = HashDigest(length=8)

    def __init__(self, *, method):
        self.ff = FakerGenerator(method=method)
        super().__init__(method=method)


class Quux3Generator(CustomGenerator):
    """
    Custom generator with custom __tohu_items_name__ and __fields__ attributes,
    where __fields__ is only a subset of the defined tohu generators.
    """
    __tohu_items_name__ = 'MyQuux3Item'
    __fields__ = ['xx', 'zz']

    xx = Integer(1, 7)
    zz = FakerGenerator(method="name")

    def __init__(self, length):
        self.yy = HashDigest(length=length)
        super().__init__(length)


class Quux4Generator(CustomGenerator):
    """
    Custom generator with custom __fields__ that are only a subset
    of the defined tohu generators, and also has them in a different
    order than they appear in the class definition (this order should
    be reflected in the generated items later).
    """

    __fields__ = ["bb", "dd", "cc"]

    aa = Constant("foobar")
    bb = HashDigest(length=8)
    cc = FakerGenerator(method="name")
    dd = Integer(100, 200)


EXEMPLAR_CUSTOM_GENERATORS = [
    Quux1Generator(),
    Quux2Generator(method="name"),
    Quux3Generator(length=10),
    Quux4Generator(),
]
