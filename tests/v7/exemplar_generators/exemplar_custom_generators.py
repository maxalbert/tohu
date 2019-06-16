from ..context import tohu
from tohu.v7.primitive_generators import Integer, HashDigest, FakerGenerator
from tohu.v7.custom_generator import CustomGenerator

__all__ = ["EXEMPLAR_CUSTOM_GENERATORS", "quux1_generator"]


# class Quux1Generator(CustomGenerator):
#     """
#     Basic custom generator with all field generators defined on the class.
#     """
#
#     aa = Integer(1, 7)
#     bb = HashDigest(length=8)
#     cc = FakerGenerator(method="name")

quux1_generator = CustomGenerator(tohu_items_name="Quux1")
quux1_generator.add_field_generator("aa", Integer(1, 7))
quux1_generator.add_field_generator("bb", HashDigest(length=6))
quux1_generator.add_field_generator("cc", FakerGenerator(method="name"))


EXEMPLAR_CUSTOM_GENERATORS = [quux1_generator]
