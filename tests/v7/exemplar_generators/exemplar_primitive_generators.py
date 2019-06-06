import os

from .helpers import check_each_generator_class_has_at_least_one_exemplar_instance

from ..context import tohu
from tohu.v7.primitive_generators import Boolean, Constant, Incremental, Integer, HashDigest, FakerGenerator

here = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(here, "..", "..", "..", "tohu", "data")
geojson_sample_file = os.path.join(data_dir, "admin_0_countries.geojson")


EXEMPLAR_PRIMITIVE_GENERATORS = [
    Constant("quux").set_tohu_name("g_constant"),
    Boolean(p=0.8).set_tohu_name("g_boolean"),
    Incremental(start=200, step=4).set_tohu_name("g_incremental"),
    Integer(100, 200).set_tohu_name("g_integer"),
    HashDigest(length=8).set_tohu_name("g_hashdigest"),
    FakerGenerator(method="name").set_tohu_name(("g_fakergenerator")),
]


check_each_generator_class_has_at_least_one_exemplar_instance(
    "tohu.v7.primitive_generators", EXEMPLAR_PRIMITIVE_GENERATORS, exclude_classes=[]
)
